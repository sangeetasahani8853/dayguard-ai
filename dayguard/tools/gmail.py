import logging
from typing import List, Dict, Any, Optional
from dayguard.tools.base import (
    SwytchcodeBaseAdapter,
    SwytchcodeValidationError,
    SwytchcodeAPIError,
    SwytchcodeAuthError
)

logger = logging.getLogger("DayGuard.Tools.Gmail")

class GmailAdapter(SwytchcodeBaseAdapter):
    """Swytchcode Adapter for Gmail calendar events and schedule retrieval."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = True
    ):
        super().__init__(
            service_name="Gmail",
            api_key=api_key,
            base_url=base_url or "https://api.swytchcode.com/v1/gmail",
            use_mock=use_mock
        )

    def get_calendar_events(self, date_str: str = "today", scenario: str = "rainy") -> List[Dict[str, Any]]:
        """
        Retrieves scheduled events and client meetings for the specified date.

        Args:
            date_str (str): Date filter (e.g. "today", "2026-09-26").
            scenario (str): Simulation scenario for mock mode ("rainy", "clear", "no_events").

        Returns:
            List[Dict[str, Any]]: List of structured calendar event objects.
        """
        valid_date = self._validate_non_empty(date_str, "date_str")
        logger.info(f"[GmailAdapter] Fetching calendar events for date='{valid_date}' (scenario: '{scenario}')")

        if self.use_mock:
            if scenario == "no_events":
                return []
            return [
                {
                    "id": "evt_101",
                    "title": "Client Strategy Meeting",
                    "start_time": "11:00 AM",
                    "end_time": "12:00 PM",
                    "location": "Gurgaon Office",
                    "is_important": True,
                    "attendees": ["client@acme.com", "user@company.com"],
                    "provider": "Swytchcode-Gmail-Mock"
                }
            ]

        response = self._make_request("GET", "events", params={"date": valid_date})
        raw_events = response.get("items", [])
        
        events = []
        for item in raw_events:
            events.append({
                "id": item.get("id", "evt_unknown"),
                "title": item.get("summary", "Untitled Meeting"),
                "start_time": item.get("start", {}).get("dateTime", "Unknown"),
                "end_time": item.get("end", {}).get("dateTime", "Unknown"),
                "location": item.get("location", "Not specified"),
                "is_important": item.get("importance", "HIGH") == "HIGH",
                "attendees": [a.get("email") for a in item.get("attendees", [])],
                "provider": "Swytchcode-Gmail-Live"
            })
        return events

# Alias for backwards compatibility
GmailTool = GmailAdapter
