"""Pydantic schemas for Artifacts."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ArtifactCreate(BaseModel):
    session_id: str
    message_id: Optional[str] = None
    artifact_type: str = Field(..., description="'markdown', 'html', or 'css'")
    title: str = Field(..., max_length=255)
    content: str = Field(..., description="Complete artifact content")
    meta_info: Optional[Dict[str, Any]] = None


class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    message_id: Optional[str] = None
    artifact_type: str
    title: str
    content: str
    meta_info: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
