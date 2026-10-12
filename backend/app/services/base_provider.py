"""Base abstract class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # 'system', 'user', 'assistant'
    content: str


class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    latency_ms: float
    token_usage: Dict[str, int] = {}
    is_fallback: bool = False
    raw_response: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract interface that every LLM provider (Ollama, Claude, OpenAI, Mock) must implement."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Generates a text completion given conversation history and system instructions."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Probes the provider service and returns health diagnostics."""
        pass
