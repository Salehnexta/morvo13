import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.post(
        "/v1/auth/register", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_login_access_token(client: AsyncClient, db_session: AsyncSession) -> None:
    # First, register a user
    await client.post(
        "/v1/auth/register", json={"email": "test_login@example.com", "password": "password123"}
    )

    response = await client.post(
        "/v1/auth/login/access-token",
        data={"username": "test_login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
