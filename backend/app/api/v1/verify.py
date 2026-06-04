from fastapi import APIRouter
from app.schemas.rewrite import RewriteOutput
from app.schemas.testOutcome import TestExecutionOutput
from agents.testing.agent import TestingAgent
from agents.verification.agent import VerificationAgent

router = APIRouter(prefix="/verify", tags=["verify"])

testing_agent = TestingAgent()
verification_agent = VerificationAgent()

@router.post("/rewrite" , response_model=TestExecutionOutput)
async def verify_rewritten_code(rewritten: RewriteOutput):
    # 1. Generate tests
    generated = await testing_agent.generate_with_evidence(rewritten.python_code)
    test_code = generated.test_code

    # 2. Run verification
    result = await verification_agent.verify(rewritten.python_code, test_code)

    # 3. return structured result
    return TestExecutionOutput(
        test_code=test_code,
        execution_result=result,
        rag_references=list(generated.evidence.references),
        retrieval_queries=list(generated.evidence.queries),
    )

