from pydantic import ValidationError
from app.schemas.explanation import ExplanationOutput

def parse_explanation_output(row_output : dict) -> ExplanationOutput:
    """
    Validates and parses LLM output into ExplanationOutput schema . 
    Raises ValidationError if output is invalid 
    """
    try :
        return ExplanationOutput(**row_output)
    except ValidationError as e:
        raise ValueError(f"Invalid explanation output from LLM: {e}")