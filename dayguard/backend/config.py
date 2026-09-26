import os
import logging
from typing import Optional, Dict, Any, List
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class SecretRedactingFormatter(logging.Formatter):
    """Custom logging formatter that redacts sensitive values from log output."""
    
    def __init__(self, fmt: str = None, datefmt: str = None, secrets_to_redact: List[str] = None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.secrets_to_redact = [s for s in (secrets_to_redact or []) if s and len(s) > 3]

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        for secret in self.secrets_to_redact:
            if secret in formatted:
                formatted = formatted.replace(secret, f"{secret[:3]}...[REDACTED]")
        return formatted

def setup_logging(level: str = "INFO", secrets: List[str] = None) -> logging.Logger:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("DayGuard")
    logger.setLevel(numeric_level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = SecretRedactingFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            secrets_to_redact=secrets
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

class Settings(BaseSettings):
    """Secure application settings loaded strictly from environment variables."""

    # Core App Configuration
    app_name: str = "DayGuard"
    environment: str = "development"
    log_level: str = "INFO"
    port: int = 8000
    
    # Mode Control: True = Deterministic Demo Mode, False = Live Swytchcode APIs
    demo_mode: bool = True
    use_mock_tools: bool = True

    # Required Credentials & Integration Tokens (Never hardcoded)
    llm_api_key: Optional[SecretStr] = None
    llm_model: str = "gpt-4o-mini"
    swytchcode_api_key: Optional[SecretStr] = None

    openweather_api_key: Optional[SecretStr] = None
    gmail_access_token: Optional[SecretStr] = None
    notion_token: Optional[SecretStr] = None
    slack_token: Optional[SecretStr] = None
    resend_api_key: Optional[SecretStr] = None

    demo_user_email: str = "demo@dayguard.ai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    def mask_secret(self, secret: Optional[SecretStr]) -> str:
        """Returns a safe, masked string representation of a SecretStr."""
        if not secret:
            return "[NOT SET]"
        val = secret.get_secret_value()
        if len(val) <= 6:
            return "******"
        return f"{val[:3]}...{val[-3:]}"

    def get_masked_summary(self) -> Dict[str, Any]:
        """Returns configuration state with all secrets securely masked."""
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "log_level": self.log_level,
            "demo_mode": self.demo_mode,
            "use_mock_tools": self.use_mock_tools or self.demo_mode,
            "llm_model": self.llm_model,
            "llm_api_key": self.mask_secret(self.llm_api_key),
            "swytchcode_api_key": self.mask_secret(self.swytchcode_api_key),
            "openweather_api_key": self.mask_secret(self.openweather_api_key),
            "gmail_access_token": self.mask_secret(self.gmail_access_token),
            "notion_token": self.mask_secret(self.notion_token),
            "slack_token": self.mask_secret(self.slack_token),
            "resend_api_key": self.mask_secret(self.resend_api_key),
            "demo_user_email": self.demo_user_email,
        }

    def validate_configuration(self) -> List[str]:
        """Validates configuration; raises ValueError if production mode is missing secrets."""
        missing_keys = []
        required_vars = [
            ("LLM_API_KEY", self.llm_api_key),
            ("SWYTCHCODE_API_KEY", self.swytchcode_api_key),
            ("OPENWEATHER_API_KEY", self.openweather_api_key),
            ("GMAIL_ACCESS_TOKEN", self.gmail_access_token),
            ("NOTION_TOKEN", self.notion_token),
            ("SLACK_TOKEN", self.slack_token),
            ("RESEND_API_KEY", self.resend_api_key),
        ]

        for var_name, var_value in required_vars:
            if not var_value or not var_value.get_secret_value().strip():
                missing_keys.append(var_name)

        if missing_keys and not self.demo_mode:
            raise ValueError(
                f"Missing required production credentials for LIVE MODE: {', '.join(missing_keys)}. "
                "Set these in environment variables or set DEMO_MODE=true."
            )

        return missing_keys

settings = Settings()

_secrets_list = []
for secret_field in [
    settings.llm_api_key,
    settings.swytchcode_api_key,
    settings.openweather_api_key,
    settings.gmail_access_token,
    settings.notion_token,
    settings.slack_token,
    settings.resend_api_key,
]:
    if secret_field:
        _secrets_list.append(secret_field.get_secret_value())

logger = setup_logging(settings.log_level, secrets=_secrets_list)
