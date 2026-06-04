"""Small retrieval smoke benchmark; optional live generation never runs generated code."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from agents.testing.query_builder import RetrievalQuery
from agents.testing.retriever import Retriever


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    retriever = Retriever(max_chunks=3)
    cases = [
        ("boundary_design", RetrievalQuery("boundary value analysis equivalence partitioning numeric minimum maximum", ("test_design",)), {"istqb"}),
        ("pytest_parameters", RetrievalQuery("pytest mark parametrize multiple inputs expected outputs", ("python_testing",)), {"pytest-parametrize"}),
        ("cobol_mocks", RetrievalQuery("COBOL unit testing mocks external CALL PERFORM paragraphs", ("language_testing",), "cobol"), {"cobol-approach-to-mocks", "cobol-test-suite-syntax"}),
        ("fortran_tolerance", RetrievalQuery("Fortran unit tests assertEqual tolerance real-valued arrays setup teardown", ("language_testing",), "fortran"), {"cime-fortran", "lfric-fortran", "pfunit"}),
        ("decimal_rounding", RetrievalQuery("Decimal quantize rounding modes ROUND_HALF_UP precision", ("numeric_testing",)), {"python-decimal"}),
        ("array_comparison", RetrievalQuery("assert_allclose array shape rtol atol equal_nan strict", ("numeric_testing",)), {"numpy-allclose"}),
        ("gnucobol_rounding", RetrievalQuery("COMPUTE ROUNDED ON SIZE ERROR receiving field", ("language_semantics",), "cobol", "gnucobol"), {"gnucobol"}),
    ]
    results = []
    for name, query, expected in cases:
        evidence = retriever.retrieve([query])
        found = {r["id"] for r in evidence.references}
        results.append({"case": name, "passed": bool(found & expected),
                        "source_ids": sorted(found), "preview": evidence.context[:500]})
    report = {"scope": "Retrieval relevance smoke checks; not a measurement of generated test quality",
              "sources": len(retriever.manifest["sources"]), "chunks": len(retriever.chunks),
              "checks": results}
    if args.live:
        from dotenv import load_dotenv
        from agents.testing.agent import TestingAgent
        load_dotenv(BACKEND / ".env")
        async def generate():
            # Use the full context budget for generation, not the benchmark's top-three limit.
            agent = TestingAgent(retriever=Retriever())
            return await agent.generate_with_evidence(
                "def add(a, b):\n    return a + b\n", language="cobol",
                legacy_code="01 A PIC S9(3).\n01 B PIC S9(3).\n01 TOTAL PIC S9(4).\nCOMPUTE TOTAL = A + B.",
                explanation={"purpose": "Add two signed three-digit integers into a four-digit result", "assumptions": []},
                verified_examples=[{"inputs": {"a": 2, "b": 3}, "expected": 5}])
        try:
            generated = asyncio.run(asyncio.wait_for(generate(), timeout=110))
            output = BACKEND / "artifacts/testing_rag_live_tests.py"
            output.write_text(generated.test_code, encoding="utf-8")
            report["live_generation"] = {"passed": True, "artifact": str(output.relative_to(BACKEND)),
                                         "scope": "Generated code passed static contract checks; not executed"}
        except Exception as exc:
            # Do not log provider messages that may include credentials or request contents.
            report["live_generation"] = {"passed": False, "error_type": type(exc).__name__}
    output = BACKEND / "artifacts/testing_rag_evaluation.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all(r["passed"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
