from pydantic import BaseModel


class ExecutionResult(BaseModel):
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool