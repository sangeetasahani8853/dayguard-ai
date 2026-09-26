import os
import logging
import pytest
from pydantic import SecretStr
from dayguard.backend.config import Settings, SecretRedactingFormatter

def test_config_defaults_and_masking():
    settings = Settings(
        llm_api_key=SecretStr("sk-test123456789key"),
        openweather_api_key=SecretStr("ow-secret-key-xyz"),
        use_mock_tools=True
    )
    
    masked = settings.get_masked_summary()
    
    assert masked["llm_api_key"] == "sk-...key"
    assert masked["openweather_api_key"] == "ow-...xyz"
    assert masked["gmail_access_token"] == "[NOT SET]"
    assert "sk-test123456789key" not in str(settings)

def test_config_validation_mock_mode():
    settings = Settings(demo_mode=True, use_mock_tools=True)
    missing = settings.validate_configuration()
    assert isinstance(missing, list)

def test_config_validation_production_mode_raises():
    settings = Settings(demo_mode=False, use_mock_tools=False)
    with pytest.raises(ValueError, match="Missing required production credentials"):
        settings.validate_configuration()

def test_secret_redacting_log_formatter():
    formatter = SecretRedactingFormatter(
        fmt="%(message)s",
        secrets_to_redact=["super_secret_token_12345"]
    )
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Attempting API call with token super_secret_token_12345",
        args=(),
        exc_info=None
    )

    formatted = formatter.format(record)
    assert "super_secret_token_12345" not in formatted
    assert "[REDACTED]" in formatted
