import logging
from typing import Dict, Any, Optional
from dayguard.tools.base import (
    SwytchcodeBaseAdapter,
    SwytchcodeValidationError,
    SwytchcodeAPIError,
    SwytchcodeAuthError
)

logger = logging.getLogger("DayGuard.Tools.Slack")

class SlackAdapter(SwytchcodeBaseAdapter):
    """Swytchcode Adapter for dispatching instant notifications to Slack channels."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = True
    ):
        super().__init__(
            service_name="Slack",
            api_key=api_key,
            base_url=base_url or "https://api.swytchcode.com/v1/slack",
            use_mock=use_mock
        )

    def send_message(self, message: str, channel: str = "#alerts") -> Dict[str, Any]:
        """
        Posts a real-time notification alert message to Slack.

        Args:
            message (str): Text body of alert.
            channel (str): Target Slack channel (e.g. "#alerts").

        Returns:
            Dict[str, Any]: Delivery status object.
        """
        valid_msg = self._validate_non_empty(message, "message")
        valid_channel = self._validate_non_empty(channel, "channel")

        logger.info(f"[SlackAdapter] Dispatching notification to channel '{valid_channel}'")

        if self.use_mock:
            return {
                "status": "success",
                "channel": valid_channel,
                "message_ts": "1727337600.000100",
                "delivered": True,
                "provider": "Swytchcode-Slack-Mock"
            }

        payload = {"channel": valid_channel, "text": valid_msg}
        response = self._make_request("POST", "messages", json_data=payload)
        return {
            "status": "success",
            "channel": valid_channel,
            "message_ts": response.get("ts", "ts_live"),
            "delivered": True,
            "provider": "Swytchcode-Slack-Live"
        }

# Alias for backwards compatibility
SlackTool = SlackAdapter
