import pytest
from dayguard.tools.base import (
    SwytchcodeValidationError,
    SwytchcodeAuthError,
    SwytchcodeAPIError
)
from dayguard.tools.weather import OpenWeatherAdapter
from dayguard.tools.gmail import GmailAdapter
from dayguard.tools.notion import NotionAdapter
from dayguard.tools.slack import SlackAdapter
from dayguard.tools.resend import ResendAdapter

# 1. OpenWeatherAdapter Tests
def test_openweather_adapter_valid_mock():
    adapter = OpenWeatherAdapter(use_mock=True)
    res = adapter.get_forecast("Gurgaon", scenario="rainy")
    assert res["location"] == "Gurgaon"
    assert res["severity"] == "HIGH"
    assert "condition" in res

def test_openweather_adapter_validation_error():
    adapter = OpenWeatherAdapter(use_mock=True)
    with pytest.raises(SwytchcodeValidationError):
        adapter.get_forecast("   ")  # empty whitespace location

def test_openweather_adapter_live_auth_error():
    adapter = OpenWeatherAdapter(api_key=None, use_mock=False)
    with pytest.raises(SwytchcodeAuthError):
        adapter.get_forecast("Gurgaon")

# 2. GmailAdapter Tests
def test_gmail_adapter_valid_mock():
    adapter = GmailAdapter(use_mock=True)
    events = adapter.get_calendar_events(date_str="today")
    assert isinstance(events, list)
    assert len(events) > 0
    assert "title" in events[0]

def test_gmail_adapter_validation_error():
    adapter = GmailAdapter(use_mock=True)
    with pytest.raises(SwytchcodeValidationError):
        adapter.get_calendar_events(date_str="")

# 3. NotionAdapter Tests
def test_notion_adapter_profile_and_task_creation():
    adapter = NotionAdapter(use_mock=True)
    profile = adapter.get_user_profile()
    assert profile["commute_mode"] == "Bike"
    
    task = adapter.create_task(title="Prep Task", description="Leave early", priority="High")
    assert task["status"] == "success"
    assert task["title"] == "Prep Task"

def test_notion_adapter_validation_error():
    adapter = NotionAdapter(use_mock=True)
    with pytest.raises(SwytchcodeValidationError):
        adapter.create_task(title="", description="Valid desc")

# 4. SlackAdapter Tests
def test_slack_adapter_send_message():
    adapter = SlackAdapter(use_mock=True)
    res = adapter.send_message(message="Alert: Rain expected", channel="#alerts")
    assert res["status"] == "success"
    assert res["channel"] == "#alerts"

def test_slack_adapter_validation_error():
    adapter = SlackAdapter(use_mock=True)
    with pytest.raises(SwytchcodeValidationError):
        adapter.send_message(message="")

# 5. ResendAdapter Tests
def test_resend_adapter_send_email():
    adapter = ResendAdapter(use_mock=True)
    res = adapter.send_email(to_email="user@company.com", subject="Alert", html_body="<p>Rain</p>")
    assert res["status"] == "success"
    assert res["to"] == "user@company.com"

def test_resend_adapter_invalid_email_validation_error():
    adapter = ResendAdapter(use_mock=True)
    with pytest.raises(SwytchcodeValidationError, match="Invalid email format"):
        adapter.send_email(to_email="not-an-email", subject="Alert", html_body="Body")
