"""Configuration management for The Lenny Growth Assistant."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Root path of the project (parent of backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    APP_NAME: str = "The Lenny Growth Assistant"

    # LLM Provider Configuration ('ollama', 'anthropic', or 'openai')
    LLM_PROVIDER: str = "ollama"

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0

    # Cloud LLM Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Fallback to mock provider if chosen provider is unavailable
    ALLOW_MOCK_FALLBACK: bool = True

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant"
    ENABLE_SQLITE_FALLBACK: bool = True
    SQLITE_DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'lenny_assistant.db'}"

    # Knowledge Base & Retrieval
    DATA_DIR: str = str(BASE_DIR / "data")
    FIXTURES_DIR: str = str(BASE_DIR / "data" / "fixtures")
    SIMILARITY_THRESHOLD: float = 0.45
    TOP_K_CHUNKS: int = 4
    MAX_CONTEXT_TOKENS: int = 3500

    # Security & CORS
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000"
    SECRET_KEY: str = "lenny-dev-secret-key-change-in-production"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
