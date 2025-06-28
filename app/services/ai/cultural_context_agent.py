import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class CulturalContextAgent:
    def __init__(self) -> None:
        # Load cultural data, common Saudi terms, Islamic principles, etc.
        # This could be from a JSON file, database, or hardcoded for now.
        self.saudi_terms = [
            "السعودية",
            "الرياض",
            "جدة",
            "الدمام",
            "المملكة",
            "رمضان",
            "عيد",
            "اليوم الوطني",
            "حلال",
            "إن شاء الله",
            "ما شاء الله",
            "أهلاً وسهلاً",
        ]
        self.islamic_principles = ["حلال", "ربا", "غرر", "ميسر", "زكاة", "صدقة"]
        self.cultural_calendar = {
            "ramadan": {"start": "2025-02-28", "end": "2025-03-29"},  # Example dates
            "eid_al_fitr": {"start": "2025-03-30", "end": "2025-04-02"},
            "eid_al_adha": {"start": "2025-06-05", "end": "2025-06-08"},
            "national_day": {"date": "2025-09-23"},
        }

    def _is_arabic_text(self, text: str) -> bool:
        arabic_pattern = re.compile(
            r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
        )
        return bool(arabic_pattern.search(text))

    def analyze_text_for_cultural_relevance(self, text: str) -> dict[str, Any]:
        is_arabic = self._is_arabic_text(text)
        contains_saudi_terms = any(term in text for term in self.saudi_terms)
        contains_islamic_terms = any(term in text for term in self.islamic_principles)

        # Simple scoring for demonstration
        relevance_score = 0
        if is_arabic:
            relevance_score += 3
        if contains_saudi_terms:
            relevance_score += 5
        if contains_islamic_terms:
            relevance_score += 4

        return {
            "is_arabic": is_arabic,
            "contains_saudi_terms": contains_saudi_terms,
            "contains_islamic_terms": contains_islamic_terms,
            "cultural_relevance_score": min(relevance_score, 10),  # Cap score at 10
        }

    def adapt_recommendation_for_culture(
        self, recommendation: str, user_language: str = "en"
    ) -> str:
        # Example: Add a cultural greeting or phrase
        if user_language == "ar":
            greeting = "أهلاً وسهلاً! "
        else:
            greeting = "Hello! "

        # Example: Suggest cultural calendar integration
        if "marketing campaign" in recommendation.lower():
            recommendation += " Consider aligning your campaigns with upcoming cultural events like Ramadan or Eid for maximum impact in Saudi Arabia."

        return greeting + recommendation

    def get_cultural_calendar_events(self, date: datetime = datetime.now()) -> list[str]:
        events = []
        for event, dates in self.cultural_calendar.items():
            if "date" in dates and dates["date"] == date.strftime("%Y-%m-%d"):
                events.append(event)
            elif "start" in dates and "end" in dates:
                start_date = datetime.strptime(dates["start"], "%Y-%m-%d")
                end_date = datetime.strptime(dates["end"], "%Y-%m-%d")
                if start_date <= date <= end_date:
                    events.append(event)
        return events
