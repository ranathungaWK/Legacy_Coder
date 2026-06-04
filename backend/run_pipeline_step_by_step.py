import asyncio
import sys
import json
import traceback

sys.path.append('/workspace/backend')

from agents.comprehension.agent import ComprehensionAgent
from agents.modernization.agent import ModernizationAgent
from agents.testing.agent import TestingAgent
from agents.verification.agent import VerificationAgent
from app.schemas.input import LegacyCodeInput
from execution.requirements_builder import build_requirements_from_sources
from orchestration.pipeline import ModernizationPipeline

async def main():
    print("=== STARTING PIPELINE STEP-BY-STEP ===")
    
    cobol_code = """
IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO-WORLD.

       PROCEDURE DIVISION.
       MAIN-LOGIC.
           DISPLAY 'Hello, World!'.
           STOP RUN. 
"""
    payload = LegacyCodeInput(
        language="cobol",
        code=cobol_code,
        job_id="test-cobol-1"
    )

    comp_agent = ComprehensionAgent()
    mod_agent = ModernizationAgent()
    test_agent = TestingAgent()
    ver_agent = VerificationAgent()
    pipeline = ModernizationPipeline()

    print("\n--- STEP 1: COMPREHENSION ---")
    try:
        explanation = await comp_agent.analyze(payload)
        
        # Depending on LangChain version, it might return a dict or a Pydantic model
        if isinstance(explanation, dict):
            print("Purpose:", explanation.get("purpose"))
        else:
            print("Purpose:", getattr(explanation, "purpose", ""))
            
    except Exception as e:
        print("Comprehension failed:", e)
        return

    print("\n--- STEP 2: MODERNIZATION ---")
    try:
        rewrite = await mod_agent.rewrite(payload.code, payload.language, explanation)
        
        if isinstance(rewrite, dict):
            python_code = rewrite.get("python_code", "")
        else:
            python_code = getattr(rewrite, "python_code", "")
            
        print("Rewritten Python Code:\n", python_code)
    except Exception as e:
        print("Modernization failed:", e)
        return
        
    print("\n--- STEP 3: TESTING AGENT ---")
    try:
        raw_test_code = await test_agent.generate_tests(python_code)
        print("Raw Generated Test Code from Agent:\n", raw_test_code)
        
        # This is what pipeline does:
        import re
        def _extract_code(candidate: str) -> str:
            blocks = re.findall(r"```(?:python\n)?([\s\S]*?)```", candidate, flags=re.IGNORECASE)
            if blocks:
                return "\n\n".join(b.strip() for b in blocks)
            lines = candidate.splitlines()
            for i, line in enumerate(lines):
                if re.match(r"^\s*(def |class |from |import |@|if |async |try:|with )", line):
                    return "\n".join(lines[i:])
            return candidate
            
        test_code = _extract_code(raw_test_code)
        print("\nTest Code after Pipeline extraction:\n", test_code)
        
    except Exception as e:
        print("Testing Agent failed:", e)
        return

    print("\n--- STEP 4: VERIFICATION AGENT ---")
    try:
        requirements_text = build_requirements_from_sources([python_code, test_code])
        print("Requirements:\n", requirements_text)
        
        result = await ver_agent.verify(
            rewritten_code=python_code,
            test_code=test_code,
            requirements_text=requirements_text,
            timeout=120
        )
        print("\nVerification Result:")
        print("Success:", result.success)
        print("Exit Code:", result.exit_code)
        print("Stdout:\n", result.stdout)
        print("Stderr:\n", result.stderr)
    except Exception as e:
        print("Verification Agent failed:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
