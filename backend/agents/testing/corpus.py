"""Versioned source snapshots and bounded chunks; no pickle deserialization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REFERENCES = ROOT / "references"
INDEX = ROOT / "retrieval_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SCHEMA_VERSION = 1


def load_records(folder: Path = REFERENCES / "snapshots") -> list[dict]:
    records = []
    for path in sorted(Path(folder).glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        for key in ("id", "title", "url", "category", "language", "version", "text"):
            if not record.get(key):
                raise ValueError(f"{path.name}: missing {key}")
        records.append(record)
    if not records:
        raise FileNotFoundError("No reference snapshots. Run python -m agents.testing.references.sync_sources")
    return records


def fingerprint(records: list[dict]) -> str:
    return hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def make_chunks(records: list[dict], tokenizer=None) -> list[dict]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    # Small enough for MiniLM's token window. Keep reference metadata on every chunk.
    splitter = (RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer, chunk_size=190, chunk_overlap=30) if tokenizer is not None
        else RecursiveCharacterTextSplitter(chunk_size=850, chunk_overlap=120))
    chunks = []
    for record in records:
        metadata = {k: v for k, v in record.items() if k != "text"}
        text = record["text"]
        if record["id"] == "istqb":
            # Include chapter 4, not exam administration and unrelated process material.
            import re
            matches = list(re.finditer(r"4\.1\s+Test Techniques Overview", text))
            if matches:
                start = matches[0].start()  # later occurrences can be bibliography entries
                stop = re.search(r"\n5\.?\s+Managing the Test Activities", text[start:])
                text = text[start:start + stop.start()] if stop else text[start:]
        for number, content in enumerate(splitter.split_text(text)):
            chunks.append({"id": f"{record['id']}:{number}", "text": content,
                           "metadata": metadata})
    return chunks
