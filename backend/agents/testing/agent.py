from __future__ import annotations

import ast
from dataclasses import dataclass
import logging
import os
import re

from .prompt_builder import PromptBuilder
from .query_builder import QueryBuilder
from .retriever import Retriever, RetrievalResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratedTests:
    test_code: str
    evidence: RetrievalResult


class TestingAgent:
    def __init__(self, model_name: str | None = None, *, llm=None, retriever=None):
        self._model_name = model_name or os.getenv("TESTING_MODEL", "gemini-2.5-flash")
        self.llm = llm
        self.retriever = retriever
        self.query_builder = QueryBuilder()
        self.prompt_builder = PromptBuilder()

    def _resolve_api_key(self) -> str | None:
        return (os.getenv("GOOGLE_GENAI_API_KEY_2") or os.getenv("GOOGLE_GENAI_API_KEY")
                or os.getenv("GOOGLE_API_KEY"))

    async def generate_with_evidence(self, rewritten_code: str, *, legacy_code: str = "",
                                     language: str = "unknown", explanation=None,
                                     verified_examples=None, compiler_dialect: str = "",
                                     target_runtime: str = "Python 3.11",
                                     available_dependencies: tuple[str, ...] = ("pytest",)) -> GeneratedTests:
        if not rewritten_code.strip():
            raise ValueError("Python rewrite is required")
        if "pytest" not in available_dependencies:
            raise ValueError("pytest must be available in the execution environment")
        queries = self.query_builder.build_queries(
            rewritten_code, legacy_code=legacy_code, language=language, explanation=explanation,
            compiler_dialect=compiler_dialect, available_dependencies=available_dependencies)
        # Never silently turn a RAG failure into an ungrounded generation request.
        if self.retriever is None:
            import asyncio
            self.retriever = await asyncio.to_thread(Retriever)
        evidence = await self.retriever.get_evidence(queries)
        prompt = self.prompt_builder.build(
            rewritten_code, evidence.context, legacy_code=legacy_code, language=language,
            explanation=explanation, verified_examples=verified_examples,
            compiler_dialect=compiler_dialect, target_runtime=target_runtime,
            available_dependencies=available_dependencies)
        if self.llm is None:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(model=self._model_name, temperature=0,
                                             api_key=self._resolve_api_key(), timeout=90, max_retries=2)
        logger.info("Testing RAG retrieved %s", [r["chunk_id"] for r in evidence.references])
        response = await self.llm.ainvoke(prompt)
        content = response.content
        if isinstance(content, list):
            content = "\n".join(block if isinstance(block, str) else block.get("text", "")
                                for block in content if isinstance(block, (dict, str)))
        if not isinstance(content, str):
            raise ValueError("Testing model returned no textual test code")
        test_code = self._sanitize(content)
        self._validate(test_code, available_dependencies)
        # Preserve an audit trail in the artifact, even if the model omits inline citations.
        provenance = ["# RAG references supplied to generator (not proof of application behavior):"]
        provenance.extend(f"# [{r['reference_id']}] {r['chunk_id']} {r['url']}" for r in evidence.references)
        return GeneratedTests("\n".join(provenance) + "\n\n" + test_code, evidence)

    async def generate_tests(self, rewritten_code: str, **kwargs) -> str:
        """Backward-compatible code-only API; use generate_with_evidence for provenance."""
        return (await self.generate_with_evidence(rewritten_code, **kwargs)).test_code

    @staticmethod
    def _sanitize(text: str) -> str:
        text = text.strip()
        match = re.fullmatch(r"```(?:python|py)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else text

    @staticmethod
    def _validate(test_code: str, available_dependencies: tuple[str, ...]) -> None:
        import sys
        try:
            tree = ast.parse(test_code)
            compile(tree, "<generated_tests>", "exec")
        except SyntaxError as exc:
            raise ValueError(f"Generated tests are invalid Python: {exc}") from exc
        imports = {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
        imports.update(a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names)
        if "solution" not in imports:
            raise ValueError("Tests must import solution")
        stdlib = getattr(sys, "stdlib_module_names", frozenset())
        unavailable = imports - set(available_dependencies) - set(stdlib) - {"solution", "__future__"}
        if unavailable:
            raise ValueError(f"Tests import unavailable dependencies: {', '.join(sorted(unavailable))}")
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
        functions.extend(method for cls in tree.body if isinstance(cls, ast.ClassDef) and cls.name.startswith("Test")
                         for method in cls.body if isinstance(method, ast.FunctionDef) and method.name.startswith("test_"))
        if not functions:
            raise ValueError("No collectible pytest tests generated")
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert) and isinstance(node.test, ast.Constant):
                raise ValueError("Constant placeholder assertion detected")
            if isinstance(node, ast.Attribute) and node.attr in {"skip", "skipif", "xfail", "importorskip"}:
                raise ValueError("Generated tests must not hide failures with skip/xfail")
        if not any(isinstance(n, ast.Assert) or (isinstance(n, ast.Attribute) and n.attr in {"raises", "assert_allclose", "assert_array_equal"})
                   for function in functions for n in ast.walk(function)):
            raise ValueError("Generated suite contains no assertions")

    def _ensure_not_placeholder(self, test_code: str) -> None:
        self._validate(test_code, ("pytest",))
