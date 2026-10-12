"""Automated tests for session persistence and context isolation."""

import pytest


@pytest.mark.asyncio
async def test_session_lifecycle_and_isolation(client):
    # 1. Create Session A
    res_a = await client.post("/api/sessions", json={"title": "Session A - PMF"})
    assert res_a.status_code == 201
    session_a = res_a.json()
    id_a = session_a["id"]

    # 2. Create Session B
    res_b = await client.post("/api/sessions", json={"title": "Session B - Pricing"})
    assert res_b.status_code == 201
    session_b = res_b.json()
    id_b = session_b["id"]
    assert id_a != id_b

    # 3. Post a message to Session A
    msg_res_a = await client.post("/api/chat", json={
        "session_id": id_a,
        "message": "What did Rahul Vohra say about product market fit?"
    })
    assert msg_res_a.status_code == 200
    chat_a_data = msg_res_a.json()
    assert chat_a_data["session_id"] == id_a

    # 4. Post a message to Session B
    msg_res_b = await client.post("/api/chat", json={
        "session_id": id_b,
        "message": "What did Patrick Campbell say about SaaS pricing?"
    })
    assert msg_res_b.status_code == 200
    chat_b_data = msg_res_b.json()
    assert chat_b_data["session_id"] == id_b

    # 5. Verify Session Isolation: inspect Session A history
    get_a = await client.get(f"/api/sessions/{id_a}")
    assert get_a.status_code == 200
    history_a = get_a.json()["messages"]
    contents_a = [m["content"] for m in history_a]

    # Session A must NOT contain Session B's query
    assert any("Rahul Vohra" in c for c in contents_a)
    assert not any("Patrick Campbell" in c for c in contents_a)

    # 6. Verify Session B history
    get_b = await client.get(f"/api/sessions/{id_b}")
    assert get_b.status_code == 200
    history_b = get_b.json()["messages"]
    contents_b = [m["content"] for m in history_b]

    assert any("Patrick Campbell" in c for c in contents_b)
    assert not any("Rahul Vohra" in c for c in contents_b)

    # 7. Delete Session A
    del_res = await client.delete(f"/api/sessions/{id_a}")
    assert del_res.status_code == 204

    # Session A should now return 404
    get_a_deleted = await client.get(f"/api/sessions/{id_a}")
    assert get_a_deleted.status_code == 404

    # Session B should remain intact
    get_b_intact = await client.get(f"/api/sessions/{id_b}")
    assert get_b_intact.status_code == 200
