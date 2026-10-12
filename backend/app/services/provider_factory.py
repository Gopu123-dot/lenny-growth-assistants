"""LLM Provider Factory with dynamic toggle and fallback support."""

from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.services.base_provider import BaseLLMProvider
from app.services.ollama_provider import OllamaProvider
from app.services.anthropic_provider import AnthropicProvider
from app.services.openai_provider import OpenAIProvider
from app.services.mock_provider import MockLLMProvider
from app.schemas.health import ModelInfo


class ProviderFactory:
    def __init__(self):
        self._current_provider = settings.LLM_PROVIDER.lower()
        self._current_model = None

    @property
    def active_provider_name(self) -> str:
        return self._current_provider

    @property
    def active_model_name(self) -> str:
        if self._current_model:
            return self._current_model
        if self._current_provider == "ollama":
            return settings.OLLAMA_MODEL
        elif self._current_provider == "anthropic":
            return settings.ANTHROPIC_MODEL
        elif self._current_provider == "openai":
            return settings.OPENAI_MODEL
        return "deterministic-evaluator"

    def set_active_provider(self, provider: str, model: Optional[str] = None):
        """Switches active provider and model at runtime."""
        provider_clean = provider.strip().lower()
        if provider_clean not in ["ollama", "anthropic", "openai", "mock"]:
            raise ValueError(f"Unsupported provider '{provider}'. Must be 'ollama', 'anthropic', or 'openai'.")
        self._current_provider = provider_clean
        self._current_model = model
        logger.info(f"Switched active LLM provider to: {self._current_provider} (model: {self.active_model_name})")

    def get_provider(
        self,
        override_provider: Optional[str] = None,
        override_model: Optional[str] = None,
    ) -> BaseLLMProvider:
        """Returns the appropriate LLM provider instance."""
        target_provider = (override_provider or self._current_provider).strip().lower()
        target_model = override_model or self.active_model_name

        if target_provider == "ollama":
            return OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model_name=target_model or settings.OLLAMA_MODEL,
                timeout=settings.OLLAMA_TIMEOUT_SECONDS,
            )
        elif target_provider == "anthropic":
            return AnthropicProvider(
                api_key=settings.ANTHROPIC_API_KEY,
                model_name=target_model or settings.ANTHROPIC_MODEL,
            )
        elif target_provider == "openai":
            return OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                model_name=target_model or settings.OPENAI_MODEL,
            )
        elif target_provider == "mock":
            return MockLLMProvider(model_name=target_model or "deterministic-evaluator")
        else:
            logger.warning(f"Unknown provider '{target_provider}'. Falling back to Ollama.")
            return OllamaProvider(model_name=settings.OLLAMA_MODEL)

    def get_available_models(self) -> List[ModelInfo]:
        """Returns metadata for all supported model options."""
        return [
            ModelInfo(
                id="ollama-llama3.2",
                name=f"Ollama ({settings.OLLAMA_MODEL})",
                provider="ollama",
                is_local=True,
                is_active=(self._current_provider == "ollama"),
                description="Local offline model via Ollama. Private, fast, zero cloud API cost.",
            ),
            ModelInfo(
                id="anthropic-claude",
                name="Anthropic Claude 3.5 Sonnet",
                provider="anthropic",
                is_local=False,
                is_active=(self._current_provider == "anthropic"),
                description="Cloud frontier model for high-nuance synthesis and deep reasoning.",
            ),
            ModelInfo(
                id="openai-gpt4o",
                name="OpenAI GPT-4o Mini",
                provider="openai",
                is_local=False,
                is_active=(self._current_provider == "openai"),
                description="Cloud high-efficiency model for fast generation.",
            ),
        ]


# Global provider factory singleton
provider_factory = ProviderFactory()
