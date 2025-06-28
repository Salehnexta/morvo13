"""Service for interacting with the SE Ranking API."""

import hashlib
from typing import Any, cast

import httpx

from app.core.config.settings import settings
from app.core.exceptions import ServiceError


class SERankingService:
    """
    Asynchronous service for interacting with the SE Ranking API.

    Handles API requests for SEO data, including backlink analysis and
    subscription status, using modern async practices with httpx.
    """

    def __init__(self) -> None:
        """
        Initializes the SERankingService, loading the API key from environment
        settings and preparing the httpx client and headers.
        """
        self.api_key = settings.SERANKING_API_KEY
        if not self.api_key:
            # In a production environment, you might want to log this error
            # or handle it more gracefully than raising an exception on init.
            raise ServiceError("SERANKING_API_KEY is not set in the environment.")

        self.base_url = "https://api.seranking.com/v1"
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        # It's best practice to initialize the client once and reuse it.
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    def get_api_key_hash(self) -> str:
        """
        Generates a SHA-256 hash of the API key for secure audit logging.

        Returns:
            A string containing the hex digest of the SHA-256 hash.
        """
        return hashlib.sha256(self.api_key.encode()).hexdigest()

    async def analyze_backlinks(self, domain: str) -> dict[str, Any]:
        """
        Asynchronously analyzes backlinks for a given domain.

        Args:
            domain: The domain to analyze.

        Returns:
            A dictionary containing the analysis results or an error message.
        """
        endpoint = "/backlinks/summary"
        params = {"target": domain, "mode": "domain", "source": "sa"}

        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses

            return {
                "success": True,
                "data": response.json(),
                "api_key_hash": self.get_api_key_hash(),
                "units_consumed": 1,  # Placeholder, actual consumption may vary
            }
        except httpx.HTTPStatusError as e:
            # Return a structured error for the agent to handle
            return {
                "success": False,
                "error": f"API Error: {e.response.status_code} - {e.response.text}",
                "status_code": e.response.status_code,
            }
        except httpx.RequestError as e:
            # For network errors, raise an exception to be caught by a higher-level handler
            raise ServiceError(f"Failed to connect to SE Ranking API: {e}") from e

    async def get_subscription_info(self) -> dict[str, Any]:
        """
        Asynchronously retrieves the current subscription information.

        Returns:
            A dictionary containing the subscription details.

        Raises:
            ServiceError: If the API call fails.
        """
        endpoint = "/account/subscription"
        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except httpx.HTTPStatusError as e:
            raise ServiceError(
                f"Failed to get subscription info: {e.response.status_code} - {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise ServiceError(f"Failed to connect to SE Ranking API: {e}") from e

    async def close(self) -> None:
        """Closes the httpx client session. Important for graceful shutdown."""
        await self.client.aclose()
