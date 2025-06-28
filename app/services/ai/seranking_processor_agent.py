import hashlib
import logging
import re
from typing import Any

import httpx

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


class SERankingProcessorAgent:
    def __init__(self) -> None:
        self.api_key = settings.SERANKING_API_KEY
        self.base_url = "https://api.seranking.com/v1"
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    def get_api_key_hash(self) -> str:
        return hashlib.sha256(self.api_key.encode()).hexdigest()

    async def analyze_backlinks(self, domain: str) -> dict[str, Any]:
        endpoint = "/backlinks/summary"
        params = {"target": domain, "mode": "domain", "country": "sa", "search_engine": "google.sa"}

        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()

            data = response.json()
            saudi_analysis = self._analyze_saudi_market_context(data, domain)

            return {
                "success": True,
                "data": {**data, "saudi_market_analysis": saudi_analysis},
                "api_key_hash": self.get_api_key_hash(),
                "units_consumed": 1,
                "response_time_ms": int(response.elapsed.total_seconds() * 1000),
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"SE Ranking API HTTP error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"API Error: {e.response.status_code} - {e.response.text}",
            }
        except httpx.RequestError as e:
            logger.error(f"SE Ranking API request error: {e}")
            return {"success": False, "error": f"Failed to connect to SE Ranking API: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error during SE Ranking analysis: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    def _analyze_saudi_market_context(
        self, api_data: dict[str, Any], domain: str
    ) -> dict[str, Any]:
        saudi_context: dict[str, Any] = {
            "saudi_domains_count": 0,
            "gcc_domains_count": 0,
            "arabic_anchor_texts": [],
            "saudi_government_backlinks": 0,
            "saudi_education_backlinks": 0,
            "local_relevance_score": 0.0,
        }

        try:
            if "summary" in api_data and len(api_data.get("summary", [])) > 0:
                summary: dict[str, Any] = api_data["summary"][0]

                if "top_countries" in summary:
                    for country in summary.get("top_countries", []):
                        if country.get("country", "").lower() in ["sa", "saudi arabia"]:
                            saudi_context["saudi_domains_count"] = country.get(
                                "referring_domains", 0
                            )
                        elif country.get("country", "").lower() in [
                            "ae",
                            "kw",
                            "qa",
                            "bh",
                            "om",
                            "uae",
                            "kuwait",
                            "qatar",
                            "bahrain",
                            "oman",
                        ]:
                            saudi_context["gcc_domains_count"] += country.get(
                                "referring_domains", 0
                            )

                if "top_anchors_by_backlinks" in summary:
                    for anchor in summary["top_anchors_by_backlinks"]:
                        anchor_text = anchor.get("anchor", "")
                        if self._is_arabic_text(anchor_text):
                            saudi_context["arabic_anchor_texts"].append(
                                {"text": anchor_text, "backlinks": anchor.get("backlinks", 0)}
                            )

                if "top_referring_domains" in summary:
                    for ref_domain in summary.get("top_referring_domains", []):
                        domain_name = ref_domain.get("domain", "")
                        if domain_name.endswith(".gov.sa"):
                            saudi_context["saudi_government_backlinks"] += ref_domain.get(
                                "backlinks", 0
                            )
                        elif domain_name.endswith(".edu.sa"):
                            saudi_context["saudi_education_backlinks"] += ref_domain.get(
                                "backlinks", 0
                            )

                total_referring_domains = summary.get("refdomains", 1)
                if total_referring_domains == 0:
                    total_referring_domains = 1
                
                saudi_ratio = saudi_context["saudi_domains_count"] / total_referring_domains
                gcc_ratio = saudi_context["gcc_domains_count"] / total_referring_domains
                arabic_ratio = len(saudi_context["arabic_anchor_texts"]) / max(
                    len(summary.get("top_anchors_by_backlinks", [])), 1
                )

                saudi_context["local_relevance_score"] = round(
                    (saudi_ratio * 4.0)
                    + (gcc_ratio * 2.0)
                    + (arabic_ratio * 2.0)
                    + (1.0 if saudi_context["saudi_government_backlinks"] > 0 else 0)
                    + (0.5 if saudi_context["saudi_education_backlinks"] > 0 else 0),
                    1,
                )

                if saudi_context["local_relevance_score"] > 10.0:
                    saudi_context["local_relevance_score"] = 10.0

        except Exception as e:
            logger.error(f"Error analyzing Saudi market context: {e}")

        return saudi_context

    def _is_arabic_text(self, text: str) -> bool:
        arabic_pattern = re.compile(
            r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
        )
        return bool(arabic_pattern.search(text))

    async def close(self) -> None:
        await self.client.aclose()
