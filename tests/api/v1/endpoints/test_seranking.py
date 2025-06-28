from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.seranking_tasks import analyze_website_task


@pytest.mark.asyncio
async def test_analyze_domain_queues_task(
    client: AsyncClient, authorized_client: AsyncClient, db_session: AsyncSession
) -> None:
    with patch.object(analyze_website_task, "delay") as mock_delay:
        domain = "example.com"
        response = await authorized_client.post(f"/v1/seranking/analyze/{domain}")

        assert response.status_code == 200
        assert response.json()["message"] == f"SE Ranking analysis for {domain} has been queued."
        mock_delay.assert_called_once_with(domain, "user_id_from_auth")  # Mocked user ID


@pytest.mark.asyncio
async def test_get_domain_history(
    client: AsyncClient, authorized_client: AsyncClient, db_session: AsyncSession
) -> None:
    domain = "example.com"
    response = await authorized_client.get(f"/v1/seranking/domains/{domain}/history")
    assert response.status_code == 200
    assert "history" in response.json()
