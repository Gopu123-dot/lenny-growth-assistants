"""Session lifecycle and conversation history endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.orm import Session as SessionModel, Message as MessageModel
from app.schemas.session import SessionSummary, SessionDetail, SessionCreate, MessageSchema, CitationSchema
from app.services.provider_factory import provider_factory

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionSummary])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """Returns all chat sessions ordered by latest update."""
    query = (
        select(SessionModel)
        .options(selectinload(SessionModel.messages))
        .order_by(SessionModel.updated_at.desc())
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    summaries = []
    for s in sessions:
        summaries.append(
            SessionSummary(
                id=s.id,
                title=s.title,
                active_provider=s.active_provider,
                active_model=s.active_model,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=len(s.messages),
            )
        )
    return summaries


@router.post("", response_model=SessionDetail, status_code=status.HTTP_201_CREATED)
async def create_session(req: SessionCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new independent conversation session."""
    session_id = str(uuid.uuid4())
    provider = req.active_provider or provider_factory.active_provider_name
    model = req.active_model or provider_factory.active_model_name

    session_obj = SessionModel(
        id=session_id,
        title=req.title or "New Conversation",
        active_provider=provider,
        active_model=model,
    )
    db.add(session_obj)
    await db.commit()
    await db.refresh(session_obj)

    return SessionDetail(
        id=session_obj.id,
        title=session_obj.title,
        active_provider=session_obj.active_provider,
        active_model=session_obj.active_model,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        messages=[],
    )


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves full conversation history and citations for a session."""
    query = (
        select(SessionModel)
        .options(
            selectinload(SessionModel.messages).selectinload(MessageModel.citations)
        )
        .where(SessionModel.id == session_id)
    )
    result = await db.execute(query)
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    formatted_messages = []
    for m in session_obj.messages:
        formatted_citations = [
            CitationSchema(
                id=c.id,
                episode_title=c.episode_title,
                guest_name=c.guest_name,
                source_url=c.source_url,
                chunk_id=c.chunk_id,
                similarity_score=c.similarity_score,
                snippet=c.snippet,
            )
            for c in m.citations
        ]
        formatted_messages.append(
            MessageSchema(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                meta_info=m.meta_info,
                citations=formatted_citations,
                created_at=m.created_at,
            )
        )

    return SessionDetail(
        id=session_obj.id,
        title=session_obj.title,
        active_provider=session_obj.active_provider,
        active_model=session_obj.active_model,
        created_at=session_obj.created_at,
        updated_at=session_obj.updated_at,
        messages=formatted_messages,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes a conversation session and all cascading records."""
    query = select(SessionModel).where(SessionModel.id == session_id)
    result = await db.execute(query)
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    await db.delete(session_obj)
    await db.commit()
    return None
