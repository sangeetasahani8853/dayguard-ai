import pytest
from dayguard.agent.graph import dayguard_agent
from dayguard.agent.router import should_execute_actions
from dayguard.agent.state import sanitize_state_for_ui

def test_graph_rainy_scenario():
    """Test graph execution under high-risk rainy scenario with all typed fields."""
    initial_state = {
        "user_request": "Check my day and take necessary action.",
        "mock_scenario": "rainy",
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
    
    final_state = dayguard_agent.invoke(initial_state)
    
    # Verify all required state fields exist
    assert final_state["risk_level"] == "HIGH"
    assert isinstance(final_state["risk_reason"], str)
    assert len(final_state["risk_reason"]) > 0
    assert len(final_state["actions_taken"]) == 3
    assert len(final_state["notifications_sent"]) == 2  # Slack + Resend
    assert "OpenWeather" in final_state["tools_used"]
    assert "Notion" in final_state["tools_used"]
    assert "Gmail" in final_state["tools_used"]
    assert "Slack" in final_state["tools_used"]
    assert "Resend" in final_state["tools_used"]
    assert "HIGH RISK ALERT" in final_state["final_response"]

def test_graph_clear_scenario():
    """Test graph execution under low-risk clear scenario."""
    initial_state = {
        "user_request": "Check my day and take necessary action.",
        "mock_scenario": "clear",
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
    
    final_state = dayguard_agent.invoke(initial_state)
    
    assert final_state["risk_level"] == "LOW"
    assert len(final_state["actions_taken"]) == 0
    assert len(final_state["notifications_sent"]) == 0
    assert "LOW RISK" in final_state["final_response"]

def test_state_sanitization_for_ui():
    state = {
        "user_request": "Test request",
        "api_key": "sk-secret12345",
        "notion_token": "token-xyz",
        "risk_level": "LOW"
    }
    sanitized = sanitize_state_for_ui(state)
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["notion_token"] == "[REDACTED]"
    assert sanitized["risk_level"] == "LOW"
