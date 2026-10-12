"""Ollama provider implementation for local offline LLM inference."""

import time
import httpx
from typing import List, Dict, Any, Optional
from app.services.base_provider import BaseLLMProvider, ChatMessage, LLMResponse
from app.core.config import settings
from app.core.logging import logger


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model_name: str = None, timeout: float = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        super().__init__(model_name or settings.OLLAMA_MODEL)
        self.timeout = timeout or settings.OLLAMA_TIMEOUT_SECONDS

    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        start_time = time.perf_counter()

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        for m in messages:
            formatted_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        url = f"{self.base_url}/api/chat"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000
            content = data.get("message", {}).get("content", "")

            tokens = {
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
            }

            return LLMResponse(
                content=content,
                provider="ollama",
                model=self.model_name,
                latency_ms=round(latency_ms, 2),
                token_usage=tokens,
                raw_response={"total_duration": data.get("total_duration")},
            )
        except httpx.ConnectError as err:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {err}")
            raise RuntimeError(
                f"Ollama daemon is not reachable at {self.base_url}. "
                f"Please ensure Ollama is running ('ollama serve') or pull model '{self.model_name}'."
            ) from err
        except httpx.TimeoutException as err:
            logger.error(f"Ollama request timed out after {self.timeout}s: {err}")
            raise RuntimeError(f"Ollama request timed out after {self.timeout}s.") from err
        except Exception as err:
            logger.error(f"Ollama generation failed: {err}")
            raise RuntimeError(f"Ollama generation error: {err}") from err

    async def health_check(self) -> Dict[str, Any]:
        """Probes Ollama service and checks if the model exists."""
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    has_model = any(self.model_name in m for m in models)
                    return {
                        "status": "healthy" if has_model else "degraded",
                        "base_url": self.base_url,
                        "configured_model": self.model_name,
                        "model_available": has_model,
                        "available_models": models,
                    }
                return {
                    "status": "degraded",
                    "base_url": self.base_url,
                    "error": f"HTTP status {res.status_code}",
                }
        except Exception as exc:
            return {
                "status": "unavailable",
                "base_url": self.base_url,
                "error": str(exc),
            }
