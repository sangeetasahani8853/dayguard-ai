import re
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("DayGuard.Tools.Base")

class SwytchcodeError(Exception):
    """Base exception for Swytchcode tools."""
    pass

class SwytchcodeAPIError(SwytchcodeError):
    """Raised when Swytchcode or downstream API returns an HTTP error response."""
    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint

class SwytchcodeAuthError(SwytchcodeError):
    """Raised when API credentials or tokens are missing or invalid."""
    pass

class SwytchcodeValidationError(SwytchcodeError):
    """Raised when parameter input validation fails."""
    pass

class SwytchcodeBaseAdapter:
    """Base class for all Swytchcode & Service integration adapters."""

    def __init__(
        self,
        service_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        use_mock: bool = True,
        timeout_seconds: float = 10.0,
        extra_headers: Optional[Dict[str, str]] = None,
    ):
        self.service_name = service_name
        self.api_key = api_key
        self.base_url = (base_url or f"https://api.swytchcode.com/v1/{service_name.lower()}").rstrip("/")
        self.use_mock = use_mock
        self.timeout = timeout_seconds
        self.extra_headers = extra_headers or {}

    def _validate_non_empty(self, value: str, param_name: str) -> str:
        if not value or not isinstance(value, str) or not value.strip():
            raise SwytchcodeValidationError(f"Parameter '{param_name}' must be a non-empty string.")
        return value.strip()

    def _validate_email(self, email: str, param_name: str = "email") -> str:
        cleaned = self._validate_non_empty(email, param_name)
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, cleaned):
            raise SwytchcodeValidationError(f"Invalid email format for '{param_name}': '{cleaned}'")
        return cleaned

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        headers.update(self.extra_headers)
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.use_mock:
            raise NotImplementedError("Mock mode should be intercepted before making actual HTTP requests.")

        if not self.api_key:
            raise SwytchcodeAuthError(f"Missing API key/token for adapter '{self.service_name}'.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"[{self.service_name}] Executing HTTP {method.upper()} -> url: '{url}'")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(
                    method=method.upper(),
                    url=url,
                    headers=self._get_headers(),
                    params=params,
                    json=json_data,
                )
                logger.info(f"[{self.service_name}] Response status: {response.status_code}")
                
                if response.status_code >= 400:
                    error_msg = f"{self.service_name} API call failed with HTTP {response.status_code}: {response.text[:200]}"
                    if response.status_code in (401, 403):
                        raise SwytchcodeAuthError(error_msg)
                    raise SwytchcodeAPIError(error_msg, status_code=response.status_code, endpoint=endpoint)
                
                return response.json()
        except httpx.RequestError as exc:
            logger.error(f"[{self.service_name}] HTTP Request network error: {exc}")
            raise SwytchcodeAPIError(f"Network error connecting to {self.service_name}: {str(exc)}", endpoint=endpoint)
