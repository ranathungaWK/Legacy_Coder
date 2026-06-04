"""Integration contract between the pipeline and source-aware testing agent."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.schemas.input import LegacyCodeInput
from app.schemas.rewrite import RewriteOutput
from app.schemas.verifyExecution import ExecutionResult
from agents.testing.agent import GeneratedTests
from agents.testing.retriever import RetrievalResult
from orchestration.pipeline import ModernizationPipeline


def make_pipeline(monkeypatch):
    pipeline = ModernizationPipeline()
    pipeline.comprehension_agent = SimpleNamespace(analyze=AsyncMock(return_value={"purpose": "Add integers"}))
    pipeline.modernization_agent = SimpleNamespace(rewrite=AsyncMock(return_value=RewriteOutput(
        python_code="def add(a, b): return a + b", design_notes=[], assumptions_made=[], compatibility_notes=[])))
    pipeline.verification_agent = SimpleNamespace(verify=AsyncMock(return_value=ExecutionResult(
        success=True, exit_code=0, stdout="passed", stderr="", timed_out=False)))
    monkeypatch.setattr("orchestration.pipeline.build_requirements_from_sources", lambda sources: "")
    monkeypatch.setattr("execution.requirements_builder.detect_heavy_packages", lambda *args, **kwargs: [])
    return pipeline


def test_pipeline_forwards_source_and_returns_provenance(monkeypatch):
    pipeline = make_pipeline(monkeypatch)
    evidence = RetrievalResult("[R1] reference", ({"reference_id": "R1", "url": "https://example.org"},), ("COBOL tests",))
    generate = AsyncMock(return_value=GeneratedTests(
        "from solution import add\ndef test_add():\n assert add(1, 2) == 3", evidence))
    pipeline.testing_agent = SimpleNamespace(generate_with_evidence=generate)
    payload = LegacyCodeInput(code="COMPUTE TOTAL = A + B.", language="cobol", compiler_dialect="gnucobol",
                              verified_examples=[{"inputs": [1, 2], "output": 3}])
    result = asyncio.run(pipeline.run(payload))
    assert generate.call_args.kwargs["legacy_code"] == payload.code
    assert generate.call_args.kwargs["compiler_dialect"] == "gnucobol"
    assert generate.call_args.kwargs["verified_examples"] == payload.verified_examples
    assert result["test_outcome"].rag_references[0]["reference_id"] == "R1"
    assert result["test_outcome"].retrieval_queries == ["COBOL tests"]
    assert result["test_outcome"].execution_result.success


def test_pipeline_exposes_test_generation_failure(monkeypatch):
    pipeline = make_pipeline(monkeypatch)
    pipeline.testing_agent = SimpleNamespace(generate_with_evidence=AsyncMock(side_effect=RuntimeError("Missing RAG index")))
    result = asyncio.run(pipeline.run(LegacyCodeInput(code="DISPLAY 'X'.", language="cobol")))
    assert result["test_outcome"] is None
    assert "RuntimeError" in result["testing_error"]
    pipeline.verification_agent.verify.assert_not_called()
