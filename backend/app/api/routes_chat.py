"""Chat conversational endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.orchestrator import orchestrator
from app.core.logging import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Receives user query, triggers agent routing, retrieves grounding, and returns response with citations."""
    try:
        return await orchestrator.handle_chat(req, db)
    except Exception as exc:
        logger.error(f"Error handling chat query '{req.message[:50]}...': {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(exc)}",
        )
