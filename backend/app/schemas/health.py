"""Pydantic schemas for operational health and model settings."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ComponentHealth(BaseModel):
    status: str  # "healthy", "degraded", "unavailable"
    details: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str  # "ok", "degraded", "error"
    version: str = "1.0.0"
    timestamp: str
    active_db: str
    active_provider: str
    active_model: str
    components: Dict[str, ComponentHealth]


class ProviderToggleRequest(BaseModel):
    provider: str  # 'ollama', 'anthropic', 'openai'
    model: Optional[str] = None


class ProviderToggleResponse(BaseModel):
    success: bool
    active_provider: str
    active_model: str
    message: str


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    is_local: bool
    is_active: bool
    description: str


class ModelsListResponse(BaseModel):
    active_provider: str
    active_model: str
    available_models: List[ModelInfo]
