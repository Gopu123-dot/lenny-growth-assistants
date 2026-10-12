"""Model provider configuration and toggle endpoints."""

from fastapi import APIRouter, HTTPException
from app.services.provider_factory import provider_factory
from app.schemas.health import (
    ModelsListResponse,
    ProviderToggleRequest,
    ProviderToggleResponse,
)

router = APIRouter(prefix="/api/models", tags=["Models & Providers"])


@router.get("", response_model=ModelsListResponse)
async def list_models():
    """Lists supported LLM providers and currently active selection."""
    return ModelsListResponse(
        active_provider=provider_factory.active_provider_name,
        active_model=provider_factory.active_model_name,
        available_models=provider_factory.get_available_models(),
    )


@router.post("/toggle", response_model=ProviderToggleResponse)
async def toggle_model_provider(req: ProviderToggleRequest):
    """Dynamically switches active LLM provider between Local Ollama and Cloud LLMs."""
    try:
        provider_factory.set_active_provider(req.provider, req.model)
        return ProviderToggleResponse(
            success=True,
            active_provider=provider_factory.active_provider_name,
            active_model=provider_factory.active_model_name,
            message=f"Successfully switched active LLM to {provider_factory.active_provider_name} ({provider_factory.active_model_name})",
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
