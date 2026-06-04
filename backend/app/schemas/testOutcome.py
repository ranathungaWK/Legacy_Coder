from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.verifyExecution import ExecutionResult


class TestExecutionOutput(BaseModel):
    test_code: str
    execution_result: ExecutionResult
    rag_references: list[dict] = Field(default_factory=list)
    retrieval_queries: list[str] = Field(default_factory=list)

