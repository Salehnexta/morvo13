import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_greeting(client: AsyncClient) -> None:
    """Chat endpoint should greet the user when greeting words are used."""
    payload = {"client_id": "test-client", "content": "Hello Morvo!"}
    response = await client.post("/v1/chat/message", json=payload)

    assert response.status_code == 200
    data = response.json()
    # basic shape assertions
    assert data["agent"] == "master_agent"
    assert data["message_id"].startswith("msg_")
    assert "hello" in data["content"].lower()
    # suggestions always returned
    assert data["suggestions"]


@pytest.mark.asyncio
async def test_chat_seo_branch(client: AsyncClient) -> None:
    """Chat endpoint should generate SEO-specific advice when the payload mentions SEO."""
    payload = {"client_id": "test-client", "content": "Could you give me SEO tips?"}
    response = await client.post("/v1/chat/message", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "seo" in data["content"].lower() 