from fastapi import APIRouter
from dotenv import load_dotenv
load_dotenv()

from app.schemas.input import LegacyCodeInput
from app.schemas.pipelineResponse import ModernizationPipelineResponse
from orchestration.pipeline import ModernizationPipeline

router = APIRouter(prefix="/modernize", tags=["modernize"])

pipeline = ModernizationPipeline()

@router.post("/", response_model=ModernizationPipelineResponse)
async def modernize_code(payload: LegacyCodeInput):
    """ Modernize the legacy code using the full async agent pipeline """
    result = await pipeline.run(payload)
    return result


@router.post("/pipeline", response_model=ModernizationPipelineResponse)
async def run_pipeline(payload: LegacyCodeInput):
    """Alias endpoint for explicitly invoking the modernization pipeline."""
    result = await pipeline.run(payload)
    return result