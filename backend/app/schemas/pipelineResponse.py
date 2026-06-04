from pydantic import BaseModel
from typing import Optional
from app.schemas.explanation import ExplanationOutput
from app.schemas.rewrite import RewriteOutput
from app.schemas.testOutcome import TestExecutionOutput

class ModernizationPipelineResponse(BaseModel):
    explanation: ExplanationOutput
    rewrite: RewriteOutput
    syntax_valid: bool
    syntax_error: Optional[str] = None
    test_outcome: Optional[TestExecutionOutput] = None
    testing_error: Optional[str] = None
