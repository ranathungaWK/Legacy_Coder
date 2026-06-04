from __future__ import annotations
from langchain_core.prompts import ChatPromptTemplate
from .prompts import SYSTEM_PROMPT, USER_PROMPT
from .query_builder import serialize_evidence

class PromptBuilder:
    def __init__(self, system_template: str = SYSTEM_PROMPT, user_template: str = USER_PROMPT):
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_template), ("user", user_template)])

    def build(self, code: str, context: str, *, legacy_code: str = "", language: str = "unknown",
              explanation=None, verified_examples=None, compiler_dialect: str = "",
              target_runtime: str = "Python 3.11", available_dependencies: tuple[str, ...] = ("pytest",)):
        if not code.strip():
            raise ValueError("Python rewrite is required")
        return self.prompt_template.invoke({
            "code": code, "context": context or "No references retrieved; do not fabricate citations.",
            "legacy_code": legacy_code or "Not supplied.", "language": language,
            "explanation": serialize_evidence(explanation),
            "verified_examples": serialize_evidence(verified_examples),
            "compiler_dialect": compiler_dialect or "Unknown; avoid dialect-specific assumptions.",
            "target_runtime": target_runtime, "available_dependencies": ", ".join(available_dependencies),
        })
