from pydantic import BaseModel , Field
from typing import List , Literal , Dict 


class ExplanationOutput(BaseModel):
    purpose: str = Field(... , description="Purpose of the code")
    inputs: List[Dict[str, str]] = Field(... , description="Input parameters or data sources")
    outputs: List[Dict[str, str]] = Field(... , description=" outputs produced by the code")
    assumptions: List[str] = Field(... , description="Assumptions made in the code")
    side_effects: List[str] = Field(... , description="State changes ,IO , database writes , or external effects" )
    edge_cases: List[str] = Field(... , description="Edge cases or special conditions")
    confidence_level: Literal["low", "medium", "high"] = Field(... , description="Confidence level of the analysis")
