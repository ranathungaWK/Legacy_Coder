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

