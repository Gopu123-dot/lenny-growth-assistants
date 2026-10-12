"""Pydantic schemas for Chat interactions."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.session import CitationSchema


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Active session ID or null to auto-create")
    message: str = Field(..., min_length=1, description="User prompt or question")
    provider_override: Optional[str] = Field(None, description="Optional override for LLM provider ('ollama', 'anthropic', 'openai')")
    model_override: Optional[str] = Field(None, description="Optional override for model name")


class ArtifactSummary(BaseModel):
    id: str
    artifact_type: str
    title: str
    preview_snippet: str


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str = "assistant"
    content: str
    intent: str
    citations: List[CitationSchema] = []
    artifacts: List[ArtifactSummary] = []
    suggested_follow_ups: List[str] = []
    active_provider: str
    active_model: str
    latency_ms: float
    is_grounded: bool = True
