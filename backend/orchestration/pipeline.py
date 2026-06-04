import os
import asyncio
from agents.comprehension.agent import ComprehensionAgent
from agents.modernization.agent import ModernizationAgent
from agents.testing.agent import TestingAgent
from agents.verification.agent import VerificationAgent
from app.schemas.input import LegacyCodeInput
from app.schemas.testOutcome import TestExecutionOutput
from app.schemas.explanation import ExplanationOutput
from app.schemas.rewrite import RewriteOutput
import traceback
from execution.requirements_builder import build_requirements_from_sources
import re
from app.schemas.verifyExecution import ExecutionResult

class ModernizationPipeline:
    def __init__(self):
        self.comprehension_agent = ComprehensionAgent()
        self.modernization_agent = ModernizationAgent()
        self.testing_agent = TestingAgent()
        self.verification_agent = VerificationAgent()

    async def run(self, payload: LegacyCodeInput) -> dict:
        """
        Runs the full async modernization pipeline:
        1. Comprehension (Gemini)
        2. Modernization/Rewrite (Gemini)
        3. Early Syntax Validation (Native compile)
        4. Test Generation (Google GenAI)
        5. Sandbox Verification (Docker)
        """
        # Step 1: Comprehension
        try:
            explanation = await self.comprehension_agent.analyze(payload)
        except Exception as e:
            print("Error during comprehension:")
            traceback.print_exc()
            explanation = ExplanationOutput(
                purpose="Unable to analyze code due to upstream model/service error.",
                inputs=[{"source": "request", "description": "Legacy code payload"}],
                outputs=[{"destination": "response", "description": "Fallback modernization result"}],
                assumptions=["Comprehension step failed; proceeding with fallback behavior."],
                side_effects=[f"Comprehension error: {str(e)}"],
                edge_cases=["Fallback output may be less accurate than normal pipeline output."],
                confidence_level="low",
            )

        # Step 2: Modernization (Rewrite)
        try:
            rewrite = await self.modernization_agent.rewrite(
                legacy_code=payload.code,
                language=payload.language,
                explanation=explanation
            )
        except Exception as e:
            print("Error during modernization:")
            traceback.print_exc()
            rewrite = RewriteOutput(
                python_code=(
                    "# Fallback rewrite generated because modernization failed.\n"
                    "# Original code is preserved in the request payload on the client side.\n"
                    "def modernization_fallback():\n"
                    "    return 'modernization_unavailable'\n"
                ),
                design_notes=["Returned fallback rewrite due to modernization failure."],
                assumptions_made=["LLM or upstream model service was unavailable or quota-limited."],
                compatibility_notes=[f"Modernization error: {str(e)}"],
            )

        python_code = rewrite.python_code

        # Step 3: Early Validation (Syntax Check)
        try:
            compile(python_code, "<string>", "exec")
            syntax_valid = True
            syntax_error = None
        except SyntaxError as e:
            syntax_valid = False
            syntax_error = f"SyntaxError: {str(e)}"
            # Return early with explanation and rewrite details, but no test execution/verification
            return {
                "explanation": explanation,
                "rewrite": rewrite,
                "syntax_valid": False,
                "syntax_error": syntax_error,
                "test_outcome": None
            }

        # Step 4/5: Test Generation + Verification
        try:
            test_code = await self.testing_agent.generate_tests(python_code)

            # Attempt to extract code blocks if the LLM returned prose with
            # embedded code (common when LLMs return explanations). If code
            # fences are present, use their contents; otherwise try to trim
            # leading prose until a plausible Python token appears.
            def _extract_code(candidate: str) -> str:
                # Find triple-backtick code blocks
                blocks = re.findall(r"```(?:python\n)?([\s\S]*?)```", candidate, flags=re.IGNORECASE)
                if blocks:
                    return "\n\n".join(b.strip() for b in blocks)

                # No fenced blocks: find first line that looks like code
                lines = candidate.splitlines()
                for i, line in enumerate(lines):
                    if re.match(r"^\s*(def |class |from |import |@|if |async |try:|with )", line):
                        return "\n".join(lines[i:])

                # Fallback: return original
                return candidate

            sanitized = _extract_code(test_code)

            # Validate generated tests are valid Python: fail fast with a clear message
            try:
                compile(sanitized, "<generated_tests>", "exec")
            except SyntaxError as e:
                msg = (
                    "Generated test code is not valid Python. The LLM likely returned prose or malformed code. "
                    "I attempted to extract code blocks but compilation still failed. SyntaxError: " + str(e)
                )

                execution_result = ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=msg + "\n\nOriginal LLM output:\n" + (test_code[:2000] or ""),
                    timed_out=False,
                )

                return {
                    "explanation": explanation,
                    "rewrite": rewrite,
                    "syntax_valid": True,
                    "syntax_error": None,
                    "test_outcome": TestExecutionOutput(
                        test_code=sanitized,
                        execution_result=execution_result,
                    ),
                }

            # If we sanitized (extracted) code, replace test_code with sanitized
            if sanitized.strip() and sanitized.strip() != test_code.strip():
                test_code = sanitized

            # Build best-effort requirements from imports in the rewrite and the tests
            requirements_text = build_requirements_from_sources([python_code, test_code])

            # Step 5: Verification (Docker sandbox) with optional requirements install
            sandbox_timeout = int(os.getenv("SANDBOX_TIMEOUT", "120"))
            sandbox_pip_cache = os.getenv("SANDBOX_PIP_CACHE")

            # Detect heavy or hardware-bound packages and fail fast with guidance
            from execution.requirements_builder import detect_heavy_packages

            # Default heavy size threshold: 50 MiB (packages with distribution files
            # larger than this are considered heavy). Can be overridden via
            # SANDBOX_HEAVY_SIZE_BYTES env var.
            try:
                default_threshold = 50 * 1024 * 1024
                size_threshold = int(os.getenv("SANDBOX_HEAVY_SIZE_BYTES", str(default_threshold)))
            except Exception:
                size_threshold = 50 * 1024 * 1024

            heavy = detect_heavy_packages(requirements_text or "", size_threshold_bytes=size_threshold)
            if heavy:
                # Construct a graceful ExecutionResult explaining why we aborted
                from app.schemas.verifyExecution import ExecutionResult

                msg = (
                    f"Verification aborted: detected heavy or hardware-bound packages: {', '.join(heavy)}. "
                    "Ephemeral sandbox installs for these packages often fail or require special system dependencies. "
                    "Options: provide a prebuilt sandbox image that includes these packages, increase SANDBOX_TIMEOUT, or remove these dependencies from the test run."
                )

                execution_result = ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=msg,
                    timed_out=False,
                )
            else:
                execution_result = await self.verification_agent.verify(
                    rewritten_code=python_code,
                    test_code=test_code,
                    requirements_text=requirements_text,
                    timeout=sandbox_timeout,
                    pip_cache_path=sandbox_pip_cache,
                )

            return {
                "explanation": explanation,
                "rewrite": rewrite,
                "syntax_valid": True,
                "syntax_error": None,
                "test_outcome": TestExecutionOutput(
                    test_code=test_code,
                    execution_result=execution_result
                )
            }
        except Exception as e:
            # Log the exception and return a graceful pipeline response
            print("Error during test generation/verification:")
            traceback.print_exc()

            return {
                "explanation": explanation,
                "rewrite": rewrite,
                "syntax_valid": True,
                "syntax_error": None,
                "test_outcome": None
            }
