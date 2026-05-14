from fastapi import APIRouter, Depends

from ..deps import get_orchestrator
from ..schemas import AnalyzeRequest, AnalyzeResponse, ChatRequest, ChatResponse
from ..services.orchestrator import Orchestrator

router = APIRouter(prefix="/api/v1", tags=["sdlc"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, orchestrator: Orchestrator = Depends(get_orchestrator)) -> AnalyzeResponse:
    """Generate full SDLC artifacts (summary, epics, stories, tasks, tests, ambiguity, estimation)."""
    return await orchestrator.analyze(req)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, orchestrator: Orchestrator = Depends(get_orchestrator)) -> ChatResponse:
    """Answer a free-form question grounded in the supplied requirement."""
    return await orchestrator.chat(req)
