"""Filtered multi-query dense + lexical retrieval, with bounded cited context."""
from __future__ import annotations

import asyncio
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
import re

from .corpus import EMBEDDING_MODEL, INDEX, SCHEMA_VERSION, fingerprint, load_records
from .query_builder import RetrievalQuery


@dataclass(frozen=True)
class RetrievalResult:
    context: str
    references: tuple[dict, ...]
    queries: tuple[str, ...]


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", text.lower())


@lru_cache(maxsize=1)
def embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


class Retriever:
    def __init__(self, index_path: str | Path = INDEX, *, model=None,
                 max_chunks: int = 10, max_context_chars: int = 16000):
        import numpy as np
        self.index_path = Path(index_path).resolve()
        path = self.index_path / "index.json"
        if not path.exists():
            raise FileNotFoundError("Testing RAG index missing. Run python -m agents.testing.build_index")
        self.manifest = json.loads(path.read_text(encoding="utf-8"))
        if (self.manifest.get("schema_version") != SCHEMA_VERSION
                or self.manifest.get("embedding_model") != EMBEDDING_MODEL):
            raise ValueError("Testing RAG index format/model mismatch; rebuild it")
        if self.index_path == INDEX.resolve() and self.manifest["corpus_fingerprint"] != fingerprint(load_records()):
            raise ValueError("Testing reference corpus changed; rebuild the RAG index")
        self.chunks = self.manifest["chunks"]
        self.vectors = np.load(self.index_path / "embeddings.npy", allow_pickle=False)
        if self.vectors.ndim != 2 or len(self.vectors) != len(self.chunks) or not np.isfinite(self.vectors).all():
            raise ValueError("Invalid RAG embedding matrix; rebuild it")
        self.model = model
        self.max_chunks = max_chunks
        self.max_context_chars = max_context_chars
        self.terms = [Counter(tokens(c["metadata"]["title"] + " " + c["text"])) for c in self.chunks]
        self.df = Counter(term for counts in self.terms for term in counts)
        self.avg_length = sum(sum(c.values()) for c in self.terms) / max(1, len(self.terms))

    @staticmethod
    def eligible(metadata: dict, query: RetrievalQuery) -> bool:
        if metadata["category"] not in query.categories:
            return False
        if metadata["language"] not in ("any", query.language):
            return False
        # Dialect-specific semantics are unsafe when the compiler is unknown.
        dialect = metadata.get("dialect", "")
        if dialect and metadata["category"] == "language_semantics":
            return bool(query.dialect) and dialect in query.dialect
        return not (dialect and query.dialect and dialect not in query.dialect)

    def _lexical(self, query: str, index: int) -> float:
        counts = self.terms[index]
        length = sum(counts.values())
        result = 0.0
        for term in set(tokens(query)):
            frequency = counts[term]
            if not frequency:
                continue
            idf = math.log(1 + (len(self.chunks) - self.df[term] + 0.5) / (self.df[term] + 0.5))
            result += idf * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * length / self.avg_length))
        return result

    def retrieve(self, queries: list[RetrievalQuery]) -> RetrievalResult:
        import numpy as np
        model = self.model if self.model is not None else embedding_model()
        vectors = np.asarray(model.encode([q.text for q in queries], normalize_embeddings=True), dtype="float32")
        if not queries or vectors.ndim != 2 or vectors.shape[1] != self.vectors.shape[1]:
            raise ValueError("Invalid retrieval queries or embedding dimensions")
        ranked = []
        for query, vector in zip(queries, vectors):
            candidates = [i for i, c in enumerate(self.chunks) if self.eligible(c["metadata"], query)]
            dense = sorted(candidates, key=lambda i: float(self.vectors[i] @ vector), reverse=True)[:20]
            sparse = sorted(candidates, key=lambda i: self._lexical(query.text, i), reverse=True)[:20]
            scores = Counter()
            for ranking in (dense, sparse):
                for rank, index in enumerate(ranking):
                    scores[index] += 1 / (60 + rank + 1)
            ranked.append(sorted(scores, key=scores.get, reverse=True))
        # Round-robin gives design, language and Python evidence space in the prompt.
        selected, seen, per_source = [], set(), Counter()
        for rank in range(20):
            for ranking in ranked:
                if rank >= len(ranking):
                    continue
                chunk = self.chunks[ranking[rank]]
                source = chunk["metadata"]["id"]
                if chunk["id"] in seen or per_source[source] >= 3:
                    continue
                selected.append(chunk)
                seen.add(chunk["id"])
                per_source[source] += 1
                if len(selected) == self.max_chunks:
                    break
            if len(selected) == self.max_chunks:
                break
        parts, references, size = [], [], 0
        for chunk in selected:
            meta = chunk["metadata"]
            label = f"R{len(references) + 1}"
            header = (f"[{label}] {meta['title']} | version: {meta['version']} | "
                      f"language: {meta['language']} | dialect: {meta.get('dialect', 'unspecified')}\n"
                      f"URL: {meta['url']} | chunk: {chunk['id']} | "
                      f"kind: {meta.get('content_kind', 'source')}\n"
                      f"Scope: {meta.get('note', 'Apply only when relevant.')}\n")
            part = header + chunk["text"]
            if size + len(part) + 2 > self.max_context_chars:
                continue
            references.append({"reference_id": label, "chunk_id": chunk["id"], **meta})
            parts.append(part)
            size += len(part) + 2
        if not references:
            raise RuntimeError("No eligible RAG evidence found for this request")
        return RetrievalResult("\n\n".join(parts), tuple(references), tuple(q.text for q in queries))

    async def get_evidence(self, queries: list[RetrievalQuery]) -> RetrievalResult:
        return await asyncio.to_thread(self.retrieve, queries)

    async def get_context(self, query: str) -> str:
        """Compatibility method; new generation uses get_evidence with query filters."""
        result = await self.get_evidence([RetrievalQuery(query, ("test_design", "python_testing"))])
        return result.context
