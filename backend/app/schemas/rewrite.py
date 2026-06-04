from pydantic import BaseModel , Field
from typing import List 

class RewriteOutput(BaseModel):
    python_code : str = Field(... , description="Modernized, clean Python implementation of the legacy code")
    design_notes : List[str] = Field(default_factory=list, description="Explanation of key design choices made during modernization")
    assumptions_made : List[str] = Field(default_factory=list, description="Assumptions required to safely modernize the code")
    compatibility_notes : List[str] = Field(default_factory=list, description="Behavior differences between legacy code and Python version")
    