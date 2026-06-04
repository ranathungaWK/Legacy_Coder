from execution.sandbox import run_pytest_in_docker
from app.schemas.verifyExecution import ExecutionResult

import asyncio

class VerificationAgent:

    def __init__(self , image_name: str = "sandbox-python:3.11"):
        self.image_name = image_name
    
    async def verify(self , rewritten_code: str , test_code: str, requirements_text: str | None = None, timeout: int = 120, pip_cache_path: str | None = None) -> ExecutionResult:
        """
        Runs the provided test suits against the rewrtten code inside the docker sandbox.
        """
        
        result = await asyncio.to_thread(
            run_pytest_in_docker,
            solution_code=rewritten_code,
            test_code=test_code,
            image=self.image_name,
            requirements_text=requirements_text,
            timeout=timeout,
            pip_cache_path=pip_cache_path,
        )

        return result