"""OpenAI provider implementation for cloud LLM inference."""

import time
import httpx
from typing import List, Dict, Any, Optional
from app.services.base_provider import BaseLLMProvider, ChatMessage, LLMResponse
from app.core.config import settings
from app.core.logging import logger


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        super().__init__(model_name or settings.OPENAI_MODEL)

    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please set it in .env or switch to LLM_PROVIDER=ollama."
            )

        start_time = time.perf_counter()

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        for m in messages:
            formatted_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()

            latency_ms = (time.perf_counter() - start_time) * 1000
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            return LLMResponse(
                content=content,
                provider="openai",
                model=self.model_name,
                latency_ms=round(latency_ms, 2),
                token_usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                },
                raw_response={"id": data.get("id")},
            )
        except Exception as exc:
            logger.error(f"OpenAI API call failed: {exc}")
            raise RuntimeError(f"OpenAI API error: {exc}") from exc

    async def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and len(self.api_key.strip()) > 5)
        return {
            "status": "healthy" if has_key else "degraded",
            "provider": "openai",
            "model": self.model_name,
            "api_key_configured": has_key,
            "message": "Key configured" if has_key else "Missing OPENAI_API_KEY",
        }
