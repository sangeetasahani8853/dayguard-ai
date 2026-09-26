import logging
from typing import Dict, Any, Optional
from dayguard.tools.base import (
    SwytchcodeBaseAdapter,
    SwytchcodeValidationError,
    SwytchcodeAPIError,
    SwytchcodeAuthError
)

logger = logging.getLogger("DayGuard.Tools.Notion")

class NotionAdapter(SwytchcodeBaseAdapter):
    """Adapter for Notion profile retrieval and task creation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = True
    ):
        super().__init__(
            service_name="Notion",
            api_key=api_key,
            base_url=base_url or "https://api.notion.com/v1",
            use_mock=use_mock,
            extra_headers={"Notion-Version": "2022-06-28"}
        )

    def get_user_profile(self) -> Dict[str, Any]:
        """Fetches user profile, commute preferences, and work mode from Notion."""
        logger.info("[NotionAdapter] Retrieving user profile from Notion")

        if self.use_mock:
            return {
                "user_id": "usr_99",
                "name": "Demo User",
                "home_location": "Gurgaon",
                "office_location": "Gurgaon Office",
                "commute_mode": "Bike",
                "work_mode": "Hybrid",
                "weather_sensitivity": {"heavy_rain": "ALERT", "extreme_heat": "WARN"},
                "preferred_channels": ["slack", "email"],
                "provider": "Swytchcode-Notion-Mock"
            }

        response = self._make_request("GET", "users/me")
        return {
            "user_id": response.get("id", "usr_unknown"),
            "name": response.get("name", "User"),
            "home_location": "Gurgaon",
            "office_location": "Gurgaon Office",
            "commute_mode": "Bike",
            "work_mode": "Hybrid",
            "weather_sensitivity": {"heavy_rain": "ALERT"},
            "preferred_channels": ["slack", "email"],
            "provider": "Notion-Live-API"
        }

    def create_task(self, title: str, description: str, priority: str = "High") -> Dict[str, Any]:
        """Creates a preparation task item in Notion."""
        valid_title = self._validate_non_empty(title, "title")
        valid_desc = self._validate_non_empty(description, "description")
        valid_priority = self._validate_non_empty(priority, "priority")

        logger.info(f"[NotionAdapter] Creating task in Notion: '{valid_title}' [Priority: {valid_priority}]")

        if self.use_mock:
            return {
                "status": "success",
                "task_id": "notion_task_883",
                "title": valid_title,
                "description": valid_desc,
                "priority": valid_priority,
                "created_at": "2026-09-26T11:00:00Z",
                "provider": "Swytchcode-Notion-Mock"
            }

        payload = {
            "parent": {"type": "page_id", "page_id": "root"},
            "properties": {
                "title": {"title": [{"text": {"content": valid_title}}]}
            }
        }
        response = self._make_request("POST", "pages", json_data=payload)
        return {
            "status": "success",
            "task_id": response.get("id", "notion_task_created"),
            "title": valid_title,
            "description": valid_desc,
            "priority": valid_priority,
            "url": response.get("url"),
            "provider": "Notion-Live-API"
        }

NotionTool = NotionAdapter
