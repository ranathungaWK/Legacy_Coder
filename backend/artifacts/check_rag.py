"""Compatibility entry point for the current attributable-corpus RAG checks.
The previous rag_check_results.json describes the retired custom FAISS corpus.
"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/evaluate_testing_rag.py"), run_name="__main__")
