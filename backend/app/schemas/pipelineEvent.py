from pydantic import BaseModel
from typing import Literal

class PipelineEvent(BaseModel):
    step : Literal["comprehension" , "modernization" , "testing" , "verification"]
    status : Literal["started" , "completed" , "failed"]
    payload : dict | None = None
    error : str | None = None

