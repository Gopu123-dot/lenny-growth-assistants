"""FastAPI main application entry point for The Lenny Growth Assistant."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db_engine
from app.retrieval.ingest import run_ingestion
from app.api.routes_health import router as health_router
from app.api.routes_models import router as models_router
from app.api.routes_sessions import router as sessions_router
from app.api.routes_chat import router as chat_router
from app.api.routes_artifacts import router as artifacts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing The Lenny Growth Assistant services...")

    # 1. Initialize Database & Tables
    try:
        await init_db_engine()
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}")

    # 2. Ingest transcripts into retrieval index
    try:
        stats = run_ingestion()
        logger.info(
            f"Knowledge base populated: {stats['chunks_indexed']} chunks across {stats['episodes_loaded']} episodes"
        )
    except Exception as exc:
        logger.error(f"Failed to ingest transcripts on startup: {exc}")

    logger.info("All services successfully initialized. Ready for user requests.")
    yield
    logger.info("Shutting down The Lenny Growth Assistant services...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Grounded AI Conversational Copilot and Content Synthesizer for Product and Growth Teams.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(models_router)
app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(artifacts_router)

# Mount Frontend static assets
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html not found"}
