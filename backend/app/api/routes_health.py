"""Health and operational diagnostic endpoints."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db, get_active_db_type
from app.services.provider_factory import provider_factory
from app.retrieval.index import global_index
from app.schemas.health import HealthResponse, ComponentHealth

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def check_health(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check for API, Database, LLM Providers, and Retrieval Index."""
    components = {}

    # 1. Check Database
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = ComponentHealth(
            status="healthy",
            details={"type": get_active_db_type(), "connected": True},
        )
    except Exception as exc:
        components["database"] = ComponentHealth(
            status="degraded",
            details={"error": str(exc), "connected": False},
        )

    # 2. Check Retrieval Index
    components["retrieval_index"] = ComponentHealth(
        status="healthy" if global_index.doc_count > 0 else "empty",
        details={
            "indexed_chunks": global_index.doc_count,
            "unique_terms": len(global_index.idf),
        },
    )

    # 3. Check Active LLM Provider
    provider = provider_factory.get_provider()
    try:
        prov_health = await provider.health_check()
        components["active_llm"] = ComponentHealth(
            status=prov_health.get("status", "healthy"),
            details=prov_health,
        )
    except Exception as exc:
        components["active_llm"] = ComponentHealth(
            status="degraded",
            details={"error": str(exc)},
        )

    # Determine overall status
    is_ok = all(c.status in ["healthy", "empty"] for c in components.values())
    overall_status = "ok" if is_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        active_db=get_active_db_type(),
        active_provider=provider_factory.active_provider_name,
        active_model=provider_factory.active_model_name,
        components=components,
    )
