"""Offline regression tests: routing, evidence provenance and generation contracts."""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from agents.testing.agent import TestingAgent as Agent
from agents.testing.corpus import EMBEDDING_MODEL, SCHEMA_VERSION, load_records
from agents.testing.query_builder import QueryBuilder, RetrievalQuery
from agents.testing.retriever import Retriever, RetrievalResult
from agents.testing.references.sync_sources import extract_text


class SmallEmbedding:
    def encode(self, texts, **kwargs):
        return np.array([[1.0, 0.0] for _ in texts], dtype="float32")


@pytest.fixture
def index_dir(tmp_path):
    records = [
        ("istqb", "test_design", "any", "boundary value analysis numeric limits", ""),
        ("cobol", "language_testing", "cobol", "COBOL decimal rounded testing", ""),
        ("fortran", "language_testing", "fortran", "Fortran array floating point tolerance", ""),
        ("ibm", "language_semantics", "cobol", "IBM TRUNC binary precision", "ibm"),
        ("pytest", "python_testing", "any", "pytest parametrize raises assertions", ""),
        ("decimal", "numeric_testing", "any", "Decimal quantize rounding", ""),
    ]
    chunks = [{"id": name + ":0", "text": text, "metadata": {
        "id": name, "title": name, "category": cat, "language": lang,
        "dialect": dialect, "version": "test", "url": "https://example.org/" + name,
    }} for name, cat, lang, text, dialect in records]
    (tmp_path / "index.json").write_text(json.dumps({
        "schema_version": SCHEMA_VERSION, "embedding_model": EMBEDDING_MODEL,
        "chunks": chunks,
    }), encoding="utf-8")
    np.save(tmp_path / "embeddings.npy", SmallEmbedding().encode(chunks))
    return tmp_path


def test_queries_use_source_constructs_and_separate_categories():
    queries = QueryBuilder().build_queries(
        "def interest(amount): return amount / 100", language="cobol",
        legacy_code="01 AMOUNT PIC S9(7)V99 COMP-3. COMPUTE X ROUNDED = AMOUNT / 100 ON SIZE ERROR DISPLAY 'ERR'.")
    assert len(queries) == 4
    assert "COMP-3" in queries[1].text
    assert "ON SIZE ERROR" in queries[1].text
    assert queries[0].categories == ("test_design",)
    assert not any("property_testing" in q.categories for q in queries)


def test_language_and_dialect_filters_and_category_diversity(index_dir):
    retriever = Retriever(index_dir, model=SmallEmbedding())
    queries = QueryBuilder().build_queries("def f(x): return x", language="cobol")
    result = retriever.retrieve(queries)
    ids = {r["id"] for r in result.references}
    assert {"istqb", "cobol", "pytest"} <= ids
    assert "fortran" not in ids and "ibm" not in ids
    ibm = retriever.retrieve([RetrievalQuery("TRUNC", ("language_semantics",), "cobol", "ibm")])
    assert ibm.references[0]["id"] == "ibm"
    assert "[R1]" in result.context and "https://example.org/" in result.context


def test_retrieval_budget_and_missing_evidence(index_dir):
    retriever = Retriever(index_dir, model=SmallEmbedding(), max_context_chars=400)
    result = retriever.retrieve([RetrievalQuery("boundary", ("test_design",))])
    assert len(result.context) <= 400
    with pytest.raises(RuntimeError, match="No eligible"):
        retriever.retrieve([RetrievalQuery("test", ("language_testing",), "java")])


def test_missing_index_fails_clearly(tmp_path):
    with pytest.raises(FileNotFoundError, match="build_index"):
        Retriever(tmp_path)


def test_corrupt_embedding_dimensions_rejected(index_dir):
    np.save(index_dir / "embeddings.npy", np.zeros((1, 2)))
    with pytest.raises(ValueError, match="embedding matrix"):
        Retriever(index_dir, model=SmallEmbedding())


class CaptureModel:
    def __init__(self, content):
        self.content = content
        self.prompt = ""

    async def ainvoke(self, prompt):
        self.prompt = prompt.to_string()
        return SimpleNamespace(content=self.content)


def test_generation_carries_original_spec_examples_and_cited_evidence(index_dir):
    llm = CaptureModel("from solution import add\ndef test_add():\n    assert add(2, 3) == 5")
    agent = Agent(llm=llm, retriever=Retriever(index_dir, model=SmallEmbedding()))
    generated = asyncio.run(agent.generate_with_evidence(
        "def add(a, b): return a + b", legacy_code="COMPUTE TOTAL = A + B.", language="cobol",
        explanation={"purpose": "Sum two values", "assumptions": ["unverified assumption"]},
        verified_examples=[{"inputs": [2, 3], "output": 5}]))
    assert "COMPUTE TOTAL" in llm.prompt
    assert "Sum two values" in llm.prompt
    assert '"output": 5' in llm.prompt
    assert "not an oracle" in llm.prompt
    assert "pytest" in llm.prompt
    assert generated.evidence.references
    assert "# [R1]" in generated.test_code
    compile(generated.test_code, "test_solution.py", "exec")


@pytest.mark.parametrize("content,message", [
    ("from solution import f\ndef test_f():\n assert True", "placeholder"),
    ("from solution import f\nimport hypothesis\ndef test_f():\n assert f() == 1", "unavailable"),
    ("from solution import f\nimport pytest\n@pytest.mark.skip\ndef test_f():\n assert f() == 1", "skip/xfail"),
    ("def test_f():\n assert 1 == 1", "import solution"),
    ("from solution import f\ndef test_f():\n pass", "no assertions"),
    ("this is not python!", "invalid Python"),
])
def test_invalid_generated_suites_rejected(content, message):
    with pytest.raises(ValueError, match=message):
        Agent._validate(content, ("pytest",))


def test_retrieval_failure_never_calls_model():
    class Broken:
        async def get_evidence(self, queries):
            raise RuntimeError("RAG unavailable")
    llm = CaptureModel("unused")
    agent = Agent(llm=llm, retriever=Broken())
    with pytest.raises(RuntimeError, match="RAG unavailable"):
        asyncio.run(agent.generate_tests("def f(): return 1"))
    assert llm.prompt == ""


def test_references_have_provenance_and_are_not_error_pages():
    records = load_records()
    assert {"cime-fortran", "istqb", "pytest-assert", "python-decimal", "numpy-allclose"} <= {r["id"] for r in records}
    for record in records:
        assert record["content_kind"] in {"downloaded_source", "curated_reference_note"}
        assert len(record["text"]) > 600
        assert record["url"].startswith("https://")


def test_html_extraction_preserves_highlighted_code():
    html = ("<html><body><article><p>" + "Reference explanation. " * 40 +
            "</p><pre><span>assert</span> <span>add</span>(2, 3) == 5\n"
            "<span>assert</span> add(0, 0) == 0</pre></article></body></html>").encode()
    text = extract_text(html, {"id": "pytest"})
    assert "assert add(2, 3) == 5\nassert add(0, 0) == 0" in text


def test_ingestion_rejects_document_shells():
    with pytest.raises(ValueError, match="No document body"):
        extract_text(b"<html><body>Access denied</body></html>", {"id": "ibm"})
