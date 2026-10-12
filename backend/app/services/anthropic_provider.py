"""Anthropic Claude provider implementation for cloud LLM inference."""

import time
import httpx
from typing import List, Dict, Any, Optional
from app.services.base_provider import BaseLLMProvider, ChatMessage, LLMResponse
from app.core.config import settings
from app.core.logging import logger


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        super().__init__(model_name or settings.ANTHROPIC_MODEL)

    async def generate(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Please set it in .env or switch to LLM_PROVIDER=ollama."
            )

        start_time = time.perf_counter()

        formatted_messages = []
        for m in messages:
            # Anthropic messages API accepts 'user' and 'assistant' roles
            role = "assistant" if m.role == "assistant" else "user"
            formatted_messages.append({"role": role, "content": m.content})

        payload = {
            "model": self.model_name,
            "max_tokens": 4096,
            "messages": formatted_messages,
            "temperature": temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Extract text blocks
            content = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    content += block.get("text", "")

            usage = data.get("usage", {})
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.model_name,
                latency_ms=round(latency_ms, 2),
                token_usage={
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                },
                raw_response={"id": data.get("id"), "stop_reason": data.get("stop_reason")},
            )
        except Exception as exc:
            logger.error(f"Anthropic API call failed: {exc}")
            raise RuntimeError(f"Anthropic API error: {exc}") from exc

    async def health_check(self) -> Dict[str, Any]:
        has_key = bool(self.api_key and len(self.api_key.strip()) > 5)
        return {
            "status": "healthy" if has_key else "degraded",
            "provider": "anthropic",
            "model": self.model_name,
            "api_key_configured": has_key,
            "message": "Key configured" if has_key else "Missing ANTHROPIC_API_KEY",
        }
