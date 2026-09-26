import pytest
import httpx
from dayguard.agent.graph import dayguard_agent
from dayguard.backend.config import Settings
from dayguard.tools.base import (
    SwytchcodeBaseAdapter,
    SwytchcodeAPIError,
    SwytchcodeAuthError,
    SwytchcodeValidationError,
)
from dayguard.tools.weather import OpenWeatherAdapter
from dayguard.tools.gmail import GmailAdapter
from dayguard.tools.notion import NotionAdapter
from dayguard.tools.slack import SlackAdapter
from dayguard.tools.resend import ResendAdapter

# 1. E2E Scenario: Heavy Rain (HIGH_RISK)
def test_e2e_heavy_rain_high_risk():
    state = {
        "user_request": "Check my day and take whatever action is necessary.",
        "mock_scenario": "rainy",
        "demo_mode": True,
        "plan": [],
        "user_context": {},
        "gmail_events": [],
        "weather": {},
        "weather_data": {},
        "risk_level": "LOW",
        "risk_reason": "",
        "reason": "",
        "risk_assessment": {},
        "recommended_actions": [],
        "selected_tools": [],
        "skipped_tools": [],
        "tools_used": [],
        "actions_completed": [],
        "actions_taken": [],
        "executed_actions": [],
        "notifications_sent": [],
        "trace_logs": [],
        "final_response": "",
    }
    
    res = dayguard_agent.invoke(state)
    
    # Assert state fields
    assert res["risk_level"] == "HIGH"
    assert "Bike" in res["user_context"]["commute_mode"]
    assert res["gmail_events"][0]["title"] == "Client Strategy Meeting"
    assert res["weather"]["condition"] == "Heavy Rain"
    assert res["selected_tools"] == ["notion", "slack", "resend"]
    assert len(res["skipped_tools"]) == 0
    assert len(res["actions_completed"]) == 3
    assert len(res["notifications_sent"]) == 2
    assert "HIGH RISK ALERT" in res["final_response"]

# 2. E2E Scenario: Clear Weather (LOW_RISK)
def test_e2e_clear_weather_low_risk():
    state = {
        "user_request": "Check my day and take whatever action is necessary.",
        "mock_scenario": "clear",
        "demo_mode": True,
        "plan": [],
        "user_context": {},
        "gmail_events": [],
        "weather": {},
        "weather_data": {},
        "risk_level": "LOW",
        "risk_reason": "",
        "reason": "",
        "risk_assessment": {},
        "recommended_actions": [],
        "selected_tools": [],
        "skipped_tools": [],
        "tools_used": [],
        "actions_completed": [],
        "actions_taken": [],
        "executed_actions": [],
        "notifications_sent": [],
        "trace_logs": [],
        "final_response": "",
    }
    
    res = dayguard_agent.invoke(state)
    
    assert res["risk_level"] == "LOW"
    assert res["selected_tools"] == []
    assert res["skipped_tools"] == ["notion", "slack", "resend"]
    assert len(res["actions_completed"]) == 0
    assert "LOW RISK" in res["final_response"]

# 3. E2E Scenario: No Gmail Events
def test_e2e_no_gmail_event():
    state = {
        "user_request": "Check my day.",
        "mock_scenario": "no_events",
        "demo_mode": True,
        "plan": [],
        "user_context": {},
        "gmail_events": [],
        "weather": {},
        "weather_data": {},
        "risk_level": "LOW",
        "risk_reason": "",
        "reason": "",
        "risk_assessment": {},
        "recommended_actions": [],
        "selected_tools": [],
        "skipped_tools": [],
        "tools_used": [],
        "actions_completed": [],
        "actions_taken": [],
        "executed_actions": [],
        "notifications_sent": [],
        "trace_logs": [],
        "final_response": "",
    }
    
    res = dayguard_agent.invoke(state)
    
    assert len(res["gmail_events"]) == 0
    assert res["risk_level"] == "HIGH" or res["risk_level"] == "LOW"

# 4. Error Case: Missing Credentials in LIVE MODE
def test_e2e_missing_credentials_live_mode():
    adapter = OpenWeatherAdapter(api_key=None, use_mock=False)
    with pytest.raises(SwytchcodeAuthError, match="Missing API key/token"):
        adapter.get_forecast("Gurgaon")

# 5. Error Case: API Failure (HTTP 500 Server Error)
def test_e2e_api_failure_handling(monkeypatch):
    class FakeResponse:
        status_code = 500
        text = "Internal Server Error"
        def json(self):
            return {}

    class FakeClient:
        def __init__(self, timeout=10.0):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def request(self, method, url, headers=None, params=None, json=None):
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)

    adapter = OpenWeatherAdapter(api_key="valid_token", use_mock=False)
    with pytest.raises(SwytchcodeAPIError) as exc_info:
        adapter.get_forecast("Gurgaon")
    assert exc_info.value.status_code == 500

# 6. Error Case: Request Timeout Handling
def test_e2e_timeout_handling(monkeypatch):
    class FakeClient:
        def __init__(self, timeout=10.0):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def request(self, method, url, headers=None, params=None, json=None):
            raise httpx.RequestError("Connection timed out", request=None)

    monkeypatch.setattr(httpx, "Client", FakeClient)

    adapter = OpenWeatherAdapter(api_key="valid_token", use_mock=False)
    with pytest.raises(SwytchcodeAPIError, match="Network error connecting"):
        adapter.get_forecast("Gurgaon")
