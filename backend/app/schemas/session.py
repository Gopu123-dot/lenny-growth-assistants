"""Pydantic schemas for Sessions and Messages."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CitationSchema(BaseModel):
    id: str
    episode_title: str
    guest_name: str
    source_url: Optional[str] = None
    chunk_id: str
    similarity_score: float
    snippet: str

    model_config = {"from_attributes": True}


class MessageSchema(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    meta_info: Optional[Dict[str, Any]] = None
    citations: List[CitationSchema] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    active_provider: Optional[str] = None
    active_model: Optional[str] = None


class SessionSummary(BaseModel):
    id: str
    title: str
    active_provider: str
    active_model: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class SessionDetail(BaseModel):
    id: str
    title: str
    active_provider: str
    active_model: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = []

    model_config = {"from_attributes": True}
