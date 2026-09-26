import pytest
from dayguard.agent.graph import dayguard_agent
from dayguard.backend.config import Settings

def test_deterministic_demo_mode_scenario():
    initial_state = {
        "user_request": "Check my day and tell me whether the weather could affect anything important.",
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
    
    res = dayguard_agent.invoke(initial_state)
    
    # Verify deterministic hackathon demo expectations
    assert res["user_context"]["commute_mode"] == "Bike"
    assert res["gmail_events"][0]["title"] == "Client Strategy Meeting"
    assert res["gmail_events"][0]["start_time"] == "11:00 AM"
    assert res["weather"]["condition"] == "Heavy Rain"
    assert res["risk_level"] == "HIGH"
    
    tool_names = [a["tool"] for a in res["actions_completed"]]
    assert "Notion" in tool_names
    assert "Slack" in tool_names
    assert "Resend" in tool_names
    assert len(res["notifications_sent"]) == 2

def test_live_mode_validation_requires_credentials():
    settings = Settings(demo_mode=False, use_mock_tools=False)
    with pytest.raises(ValueError, match="Missing required production credentials for LIVE MODE"):
        settings.validate_configuration()
