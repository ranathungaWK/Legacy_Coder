from pydantic import BaseModel
from typing import Optional
from app.schemas.verifyExecution import ExecutionResult


class TestExecutionOutput(BaseModel):
    test_code: str
    execution_result: ExecutionResult
    