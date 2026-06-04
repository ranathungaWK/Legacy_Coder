import asyncio
from dotenv import load_dotenv
load_dotenv()

from orchestration.pipeline import ModernizationPipeline
from app.schemas.input import LegacyCodeInput

async def main():
    pipeline = ModernizationPipeline()
    
    # 1. Test snippet (JavaScript addition function)
    payload = LegacyCodeInput(
        language="javascript",
        code="""
        function add(a, b) {
            return a + b;
        }
        """,
        job_id="test-e2e-001"
    )
    
    print("--- Starting End-to-End Modernization Pipeline ---")
    print(f"Legacy Code:\n{payload.code}")
    
    try:
        result = await pipeline.run(payload)
        
        print("\n--- Pipeline Result ---")
        print("\n[Comprehension Explanation]:")
        print(result["explanation"].model_dump_json(indent=2))
        
        print("\n[Modernized Python Code]:")
        print(result["rewrite"].python_code)
        print("\n[Design Notes]:")
        print(result["rewrite"].design_notes)
        
        print(f"\n[Syntax Validation]: Valid = {result['syntax_valid']}, Error = {result['syntax_error']}")
        
        if result["test_outcome"]:
            print("\n[Generated Test Code]:")
            print(result["test_outcome"].test_code)
            print("\n[Docker Sandbox Execution Result]:")
            print(result["test_outcome"].execution_result)
        else:
            print("\n[Test Outcome]: None (Pipeline exited early or skipped)")
            
    except Exception as e:
        print(f"\nPipeline execution failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
