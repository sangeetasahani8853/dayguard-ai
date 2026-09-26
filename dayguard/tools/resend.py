import logging
from typing import Dict, Any, Optional
from dayguard.tools.base import (
    SwytchcodeBaseAdapter,
    SwytchcodeValidationError,
    SwytchcodeAPIError,
    SwytchcodeAuthError
)

logger = logging.getLogger("DayGuard.Tools.Resend")

class ResendAdapter(SwytchcodeBaseAdapter):
    """Swytchcode Adapter for dispatching transactional weather advisory emails via Resend."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = True
    ):
        super().__init__(
            service_name="Resend",
            api_key=api_key,
            base_url=base_url or "https://api.swytchcode.com/v1/resend",
            use_mock=use_mock
        )

    def send_email(self, to_email: str, subject: str, html_body: str) -> Dict[str, Any]:
        """
        Sends a formatted HTML email via Resend API.

        Args:
            to_email (str): Recipient email address.
            subject (str): Email subject header.
            html_body (str): HTML content body.

        Returns:
            Dict[str, Any]: Delivery confirmation object with email ID.
        """
        valid_to = self._validate_email(to_email, "to_email")
        valid_subject = self._validate_non_empty(subject, "subject")
        valid_html = self._validate_non_empty(html_body, "html_body")

        logger.info(f"[ResendAdapter] Sending transactional email to '{valid_to}' with subject: '{valid_subject}'")

        if self.use_mock:
            return {
                "status": "success",
                "email_id": "resend_msg_99482",
                "to": valid_to,
                "subject": valid_subject,
                "delivered": True,
                "provider": "Swytchcode-Resend-Mock"
            }

        payload = {
            "to": [valid_to],
            "subject": valid_subject,
            "html": valid_html
        }
        response = self._make_request("POST", "emails", json_data=payload)
        return {
            "status": "success",
            "email_id": response.get("id", "resend_live_id"),
            "to": valid_to,
            "subject": valid_subject,
            "delivered": True,
            "provider": "Swytchcode-Resend-Live"
        }

# Alias for backwards compatibility
ResendTool = ResendAdapter
