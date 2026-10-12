"""Automated tests for Artifact generation and retrieval."""

import pytest


@pytest.mark.asyncio
async def test_artifact_generation_via_chat(client):
    # Send chat prompt asking for an HTML artifact
    chat_res = await client.post("/api/chat", json={
        "message": "Generate an interactive HTML scorecard for evaluating our onboarding funnel."
    })
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert data["intent"] == "artifact_generation"
    assert len(data["artifacts"]) > 0

    art_summary = data["artifacts"][0]
    art_id = art_summary["id"]

    # Retrieve artifact by ID
    get_art = await client.get(f"/api/artifacts/{art_id}")
    assert get_art.status_code == 200
    art_data = get_art.json()
    assert art_data["id"] == art_id
    assert art_data["artifact_type"] in ["html", "markdown"]
    assert len(art_data["content"]) > 50


@pytest.mark.asyncio
async def test_ship30_essay_generation_via_chat(client):
    # Send chat prompt asking for Ship 30 essay
    chat_res = await client.post("/api/chat", json={
        "message": "Write a Ship 30 for 30 essay on why retention breaks before acquisition."
    })
    assert chat_res.status_code == 200
    data = chat_res.json()
    assert data["intent"] == "ship30_essay"
    assert "Retention" in data["content"]
    assert len(data["artifacts"]) > 0
