"""Automated tests for model providers and runtime toggling."""

import pytest
from app.services.provider_factory import provider_factory
from app.services.mock_provider import MockLLMProvider
from app.services.ollama_provider import OllamaProvider


@pytest.mark.asyncio
async def test_provider_factory_and_toggle(client):
    # Test initial active provider
    models_res = await client.get("/api/models")
    assert models_res.status_code == 200
    data = models_res.json()
    assert "available_models" in data

    # Toggle to mock provider
    toggle_res = await client.post("/api/models/toggle", json={"provider": "mock"})
    assert toggle_res.status_code == 200
    assert toggle_res.json()["active_provider"] == "mock"
    assert provider_factory.active_provider_name == "mock"

    # Toggle to ollama
    toggle_res2 = await client.post("/api/models/toggle", json={"provider": "ollama", "model": "mistral"})
    assert toggle_res2.status_code == 200
    assert toggle_res2.json()["active_provider"] == "ollama"
    assert provider_factory.active_model_name == "mistral"

    # Test invalid provider
    invalid_res = await client.post("/api/models/toggle", json={"provider": "invalid_provider"})
    assert invalid_res.status_code == 400

    # Reset back to mock for testing
    provider_factory.set_active_provider("mock")


@pytest.mark.asyncio
async def test_mock_provider_generation():
    prov = MockLLMProvider()
    from app.services.base_provider import ChatMessage
    messages = [ChatMessage(role="user", content="What did Rahul Vohra say about PMF?")]
    res = await prov.generate(messages)
    assert "Superhuman" in res.content
    assert "40%" in res.content
    assert res.provider == "mock"
