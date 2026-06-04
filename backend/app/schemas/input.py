from __future__ import annotations
from pydantic import BaseModel ,  Field
from typing import Literal

#input schema by an user to analyze
class LegacyCodeInput(BaseModel):
    code : str = Field(... , description="Legacy source code")
    
    language : Literal ["cobol" , "fortran" , "c" , "c++" , "java" , "unknown"]

    job_id: str | None = Field(
        default=None,
        description="Job ID for tracking the analysis"
    )

    compiler_dialect: str = Field(default="", max_length=200,
        description="Source compiler/dialect and relevant options, if known")
    verified_examples: list[dict] = Field(default_factory=list,
        description="User-supplied reference input/output examples; not model-generated expectations")

