import os

from langchain_google_genai import ChatGoogleGenerativeAI
from agents.testing.prompt_builder import PromptBuilder
from agents.testing.query_builder import QueryBuilder
from agents.testing.retriever import Retriever
import re


class TestingAgent:
    def __init__(self , model_name:str = "gemini-2.5-flash") -> None:
        self._model_name = model_name
        self.llm = None

        self.retriever = None
        self.query_builder = QueryBuilder()
        self.prompt_builder = PromptBuilder()

    def _resolve_api_key(self) -> str | None:
        """Prefer the dedicated testing-agent key, then fall back to the shared key."""

        return os.getenv("GOOGLE_GENAI_API_KEY_2")

    async def generate_tests(self , rewritten_code:str) -> str:
        """ generate test cases for the rewritten code """
        search_query = self.query_builder.build_query(rewritten_code)
        # Lazy-init retriever to avoid import-time errors when vectorstore is missing
        if self.retriever is None:
            try:
                self.retriever = Retriever()
            except Exception as e:
                print("TestingAgent: retriever initialization failed:", e)
                self.retriever = None

        if self.retriever is not None:
            context = await self.retriever.get_context(search_query)
        else:
            context = ""
        prompt = self.prompt_builder.build(code = rewritten_code , context = context)
        try:
            if self.llm is None:
                # Lazy-init the Google GenAI LLM; allow failures to be caught by except
                self.llm = ChatGoogleGenerativeAI(
                    model = self._model_name,
                    temperature = 0.0,
                    convert_system_message_to_human = True,
                    api_key = self._resolve_api_key()
                )
            response = await self.llm.ainvoke(prompt)
            test_code = self._sanitize(response.content)
            self._ensure_not_placeholder(test_code)
            return test_code
        except Exception as e:
            print("TestingAgent: LLM error during test generation:", e)
            raise RuntimeError(
                "TestingAgent failed to generate tests. "
                "Fix the model/runtime issue instead of returning placeholder tests."
            ) from e

    def _sanitize(self , text:str) -> str:
        """ Robustly removes markdown code blocks """
        cleaned = text.strip()
        
        # Try to find python code blocks
        import re
        blocks = re.findall(r"```(?:python)?\s*(.*?)```", cleaned, re.DOTALL | re.IGNORECASE)
        if blocks:
            cleaned = "\n\n".join(b.strip() for b in blocks)
        else:
            # Fallback if no block is found but it starts with ```
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

        return cleaned

    def _ensure_not_placeholder(self, test_code: str) -> None:
        """Reject trivial placeholder tests that mask generation failures."""

        placeholder_patterns = [
            r"def\s+test_placeholder\s*\(",
            r"assert\s+True\b",
        ]

        if any(re.search(pattern, test_code) for pattern in placeholder_patterns):
            raise ValueError(
                "Placeholder pytest output detected. "
                "The test generator must return real assertions against solution code."
            )


