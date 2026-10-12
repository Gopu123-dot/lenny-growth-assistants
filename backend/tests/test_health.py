"""Automated tests for health and diagnostics endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Verifies that GET /api/health returns operational status and component details."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "database" in data["components"]
    assert "retrieval_index" in data["components"]
    assert "active_llm" in data["components"]
    assert data["components"]["retrieval_index"]["status"] in ["healthy", "ok"]
