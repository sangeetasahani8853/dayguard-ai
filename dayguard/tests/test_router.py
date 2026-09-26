import pytest
from dayguard.agent.graph import dayguard_agent
from dayguard.agent.router import should_execute_actions

def test_high_risk_scenario():
    initial_state = {
        "user_request": "Check my day.",
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
    
    assert final_state["risk_level"] == "HIGH"
    assert "notion" in final_state["selected_tools"]
    assert "slack" in final_state["selected_tools"]
    assert "resend" in final_state["selected_tools"]
    assert len(final_state["skipped_tools"]) == 0
    assert len(final_state["actions_completed"]) == 3
    assert len(final_state["notifications_sent"]) == 2

def test_medium_risk_scenario():
    initial_state = {
        "user_request": "Check my day.",
        "mock_scenario": "medium",
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
    
    assert final_state["risk_level"] == "MEDIUM"
    assert "notion" in final_state["selected_tools"]
    assert len(final_state["actions_completed"]) >= 2
    assert "MEDIUM RISK ADVISORY" in final_state["final_response"]

def test_low_risk_scenario():
    initial_state = {
        "user_request": "Check my day.",
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
    assert len(final_state["selected_tools"]) == 0
    assert "slack" in final_state["skipped_tools"]
    assert "resend" in final_state["skipped_tools"]
    assert len(final_state["actions_completed"]) == 0
    assert "LOW RISK" in final_state["final_response"]
