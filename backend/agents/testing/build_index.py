"""Build a safe dense index from the attributable reference corpus.

Run from backend: python -m agents.testing.build_index
The old custom knowledge_base and pickle/FAISS index are preserved but not used.
"""
from __future__ import annotations

import json
from pathlib import Path

from .corpus import (EMBEDDING_MODEL, INDEX, SCHEMA_VERSION, fingerprint,
                     load_records, make_chunks)


def load_kb_documents(folder_path):
    """Compatibility helper for older diagnostics; not the new index's corpus."""
    from langchain_core.documents import Document
    return [Document(page_content=p.read_text(encoding="utf-8"), metadata={"source": p.name})
            for p in sorted(Path(folder_path).rglob("*.txt"))]


def build_index(output_dir: Path = INDEX, *, model=None) -> dict:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    records = load_records()
    if model is None:
        model = SentenceTransformer(EMBEDDING_MODEL)
    chunks = make_chunks(records, getattr(model, "tokenizer", None))
    # Add short identifying context without displacing the actual passage.
    texts = [f"{c['metadata']['title']}: {c['text']}" for c in chunks]
    vectors = np.asarray(model.encode(texts, normalize_embeddings=True, show_progress_bar=True), dtype="float32")
    if len(vectors) != len(chunks) or not np.isfinite(vectors).all():
        raise ValueError("Invalid document embeddings")
    manifest = {"schema_version": SCHEMA_VERSION, "embedding_model": EMBEDDING_MODEL,
                "corpus_fingerprint": fingerprint(records), "chunks": chunks,
                "sources": [{k: v for k, v in r.items() if k != "text"} for r in records]}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # Write vectors before the manifest; the manifest is the index's completion marker.
    np.save(output_dir / "embeddings.npy", vectors, allow_pickle=False)
    (output_dir / "index.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    print(f"Indexed {len(records)} sources / {len(chunks)} chunks in {output_dir}")
    return manifest


if __name__ == "__main__":
    build_index()
