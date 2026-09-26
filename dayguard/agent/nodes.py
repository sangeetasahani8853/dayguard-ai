import logging
from datetime import datetime
from typing import Dict, Any, List

from dayguard.backend.config import settings
from dayguard.agent.state import DayGuardState
from dayguard.tools.gmail import GmailAdapter
from dayguard.tools.weather import OpenWeatherAdapter
from dayguard.tools.notion import NotionAdapter
from dayguard.tools.slack import SlackAdapter
from dayguard.tools.resend import ResendAdapter

logger = logging.getLogger("DayGuard.Agent.Nodes")

def _add_log(logs: List[Dict[str, Any]], step: str, message: str, status: str = "completed") -> List[Dict[str, Any]]:
    new_logs = list(logs) if logs else []
    new_logs.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "step": step,
        "message": message,
        "status": status,
    })
    return new_logs

def _add_tool_used(tools: List[str], tool_name: str) -> List[str]:
    new_tools = list(tools) if tools else []
    if tool_name not in new_tools:
        new_tools.append(tool_name)
    return new_tools

def _get_demo_mode(state: DayGuardState) -> bool:
    return state.get("demo_mode", settings.demo_mode)

def planner(state: DayGuardState) -> Dict[str, Any]:
    """Understands natural language request and determines required information & plan."""
    demo_mode = _get_demo_mode(state)
    logger.info(f"Executing Node 1: planner (Mode: {'DEMO MODE' if demo_mode else 'LIVE MODE'})")
    request = state.get("user_request", "")
    plan = [
        "1. Retrieve user profile & commute preferences from Notion",
        "2. Fetch today's client meetings from Gmail",
        "3. Check real-time & forecast weather conditions via OpenWeather",
        "4. Evaluate environmental risk by combining context, schedule, and forecast",
        "5. Conditionally execute required prep tasks & notifications",
    ]
    mode_str = "DEMO MODE (Deterministic Mock Data)" if demo_mode else "LIVE MODE (Swytchcode Production APIs)"
    logs = _add_log(state.get("trace_logs", []), "Planner", f"Parsed request: '{request}' [{mode_str}]. Formulated 5-step plan.")
    tools = _add_tool_used(state.get("tools_used", []), "Planner")
    return {"plan": plan, "trace_logs": logs, "tools_used": tools}

def context_retriever(state: DayGuardState) -> Dict[str, Any]:
    """Gets user preferences/context from Notion."""
    demo_mode = _get_demo_mode(state)
    logger.info("Executing Node 2: context_retriever")
    notion_adapter = NotionAdapter(
        api_key=settings.notion_token.get_secret_value() if settings.notion_token else None,
        use_mock=demo_mode
    )
    profile = notion_adapter.get_user_profile()
    logs = _add_log(
        state.get("trace_logs", []),
        "Notion Context",
        f"Retrieved user profile: Commute='{profile.get('commute_mode')}', Location='{profile.get('home_location')}'"
    )
    tools = _add_tool_used(state.get("tools_used", []), "Notion")
    return {"user_context": profile, "trace_logs": logs, "tools_used": tools}

def gmail_checker(state: DayGuardState) -> Dict[str, Any]:
    """Finds relevant meetings/events from Gmail."""
    demo_mode = _get_demo_mode(state)
    logger.info("Executing Node 3: gmail_checker")
    scenario = state.get("mock_scenario", "rainy")
    gmail_adapter = GmailAdapter(
        api_key=settings.gmail_access_token.get_secret_value() if settings.gmail_access_token else None,
        use_mock=demo_mode
    )
    events = gmail_adapter.get_calendar_events(scenario=scenario)
    event_titles = [e.get("title") for e in events]
    logs = _add_log(
        state.get("trace_logs", []),
        "Gmail Checker",
        f"Found {len(events)} important event(s): {', '.join(event_titles)}"
    )
    tools = _add_tool_used(state.get("tools_used", []), "Gmail")
    return {"gmail_events": events, "trace_logs": logs, "tools_used": tools}

def weather_checker(state: DayGuardState) -> Dict[str, Any]:
    """Gets current/forecast weather from OpenWeather."""
    demo_mode = _get_demo_mode(state)
    logger.info("Executing Node 4: weather_checker")
    user_context = state.get("user_context", {})
    location = user_context.get("home_location", "Gurgaon")
    scenario = state.get("mock_scenario", "rainy")
    
    weather_adapter = OpenWeatherAdapter(
        api_key=settings.openweather_api_key.get_secret_value() if settings.openweather_api_key else None,
        use_mock=demo_mode
    )
    forecast = weather_adapter.get_forecast(location=location, scenario=scenario)
    
    logs = _add_log(
        state.get("trace_logs", []),
        "Weather Checker",
        f"OpenWeather report for {location}: Condition='{forecast.get('condition')}', Rain Prob={forecast.get('rain_probability')}%"
    )
    tools = _add_tool_used(state.get("tools_used", []), "OpenWeather")
    return {
        "weather": forecast,
        "weather_data": forecast,
        "trace_logs": logs,
        "tools_used": tools
    }

def decision_engine(state: DayGuardState) -> Dict[str, Any]:
    """
    Combines Gmail + Notion + weather information.
    Determines environmental risk level (HIGH_RISK, MEDIUM_RISK, LOW_RISK).
    Decides necessary actions based on explicit policy rules.
    """
    logger.info("Executing Node 5: decision_engine")
    weather = state.get("weather", state.get("weather_data", {}))
    context = state.get("user_context", {})
    events = state.get("gmail_events", [])
    scenario = state.get("mock_scenario", "rainy").lower()
    
    commute = context.get("commute_mode", "Bike")
    rain_prob = weather.get("rain_probability", 0)
    severity = weather.get("severity", "LOW")
    preferred_channels = context.get("preferred_channels", ["slack", "email"])
    
    all_action_tools = ["notion", "slack", "resend"]
    
    recommended_actions = []
    selected_tools = []
    skipped_tools = []

    # Risk evaluation rules
    if scenario == "medium" or (rain_prob > 30 and rain_prob <= 60):
        risk_level = "MEDIUM"
        reason = f"Moderate weather risk detected ({rain_prob}% rain prob). Creating Notion task and notifying via user preference ({', '.join(preferred_channels)})."
        
        selected_tools.append("notion")
        recommended_actions.append({
            "tool": "notion",
            "action": "create_task",
            "params": {
                "title": "Advisory: Monitor Weather for Client Meeting",
                "description": "Check weather update before departure.",
                "priority": "Medium"
            }
        })
        
        if "slack" in preferred_channels:
            selected_tools.append("slack")
            recommended_actions.append({
                "tool": "slack",
                "action": "send_message",
                "params": {
                    "channel": "#alerts",
                    "message": "⚠️ DayGuard Weather Advisory: Moderate rain expected. Please check travel conditions."
                }
            })
            
        if "email" in preferred_channels or "resend" in preferred_channels:
            selected_tools.append("resend")
            recommended_actions.append({
                "tool": "resend",
                "action": "send_email",
                "params": {
                    "to": "user@company.com",
                    "subject": "DayGuard Weather Advisory",
                    "body": "Moderate rain forecast around commute time."
                }
            })
            
        skipped_tools = [t for t in all_action_tools if t not in selected_tools]

    elif scenario == "clear" or (severity == "LOW" and rain_prob <= 30):
        risk_level = "LOW"
        reason = "Weather is clear with low rain risk; normal commute conditions expected. No notifications required."
        selected_tools = []
        skipped_tools = ["notion", "slack", "resend"]
        recommended_actions = []

    else:  # HIGH_RISK (default for rainy scenario)
        risk_level = "HIGH"
        reason = f"Heavy rain expected around commute time for user travelling by {commute} to an important meeting."
        selected_tools = ["notion", "slack", "resend"]
        skipped_tools = []
        
        recommended_actions = [
            {
                "tool": "notion",
                "action": "create_task",
                "params": {
                    "title": "Prepare for 11 AM Client Meeting",
                    "description": "Leave earlier, carry rain gear, monitor commute.",
                    "priority": "High"
                }
            },
            {
                "tool": "slack",
                "action": "send_message",
                "params": {
                    "channel": "#alerts",
                    "message": "⚠️ DayGuard Weather Alert: Heavy rain expected around your 11 AM client meeting commute. Plan extra travel time."
                }
            },
            {
                "tool": "resend",
                "action": "send_email",
                "params": {
                    "to": "user@company.com",
                    "subject": "DayGuard Alert: Weather Advisory for Today's Schedule",
                    "body": "Heavy rain forecast around 10:30 AM. Notion task created & Slack alert sent."
                }
            }
        ]

    risk_assessment = {
        "risk_level": risk_level,
        "risk_reason": reason,
        "selected_tools": selected_tools,
        "skipped_tools": skipped_tools,
        "affected_events_count": len(events) if risk_level != "LOW" else 0
    }
    
    logs = _add_log(
        state.get("trace_logs", []),
        "Decision Engine",
        f"Assessed Risk: {risk_level}. Reason: {reason}. Selected tools: {selected_tools}. Skipped: {skipped_tools}."
    )
    return {
        "risk_level": risk_level,
        "risk_reason": reason,
        "reason": reason,
        "risk_assessment": risk_assessment,
        "recommended_actions": recommended_actions,
        "selected_tools": selected_tools,
        "skipped_tools": skipped_tools,
        "trace_logs": logs
    }

def action_executor(state: DayGuardState) -> Dict[str, Any]:
    """
    Conditionally calls Notion, Slack, and Resend.
    Does NOT execute all tools every time.
    """
    demo_mode = _get_demo_mode(state)
    logger.info(f"Executing Node 6: action_executor (Mode: {'DEMO MODE' if demo_mode else 'LIVE MODE'})")
    actions = state.get("recommended_actions", [])
    actions_completed = []
    notifications_sent = []
    logs = state.get("trace_logs", [])
    tools = state.get("tools_used", [])
    
    if not actions:
        logger.info("[action_executor] No recommended actions to execute.")
        logs = _add_log(logs, "Action Executor", "Skipped action execution (No actions needed for LOW_RISK).")
        return {
            "actions_completed": [],
            "actions_taken": [],
            "executed_actions": [],
            "notifications_sent": [],
            "trace_logs": logs
        }
    
    notion_adapter = NotionAdapter(
        api_key=settings.notion_token.get_secret_value() if settings.notion_token else None,
        use_mock=demo_mode
    )
    slack_adapter = SlackAdapter(
        api_key=settings.slack_token.get_secret_value() if settings.slack_token else None,
        use_mock=demo_mode
    )
    resend_adapter = ResendAdapter(
        api_key=settings.resend_api_key.get_secret_value() if settings.resend_api_key else None,
        use_mock=demo_mode
    )
    
    for act in actions:
        tool_name = act.get("tool")
        params = act.get("params", {})
        
        if tool_name == "notion":
            res = notion_adapter.create_task(
                title=params.get("title", "Prep Task"),
                description=params.get("description", ""),
                priority=params.get("priority", "High")
            )
            item = {"tool": "Notion", "action": "create_task", "result": res}
            actions_completed.append(item)
            tools = _add_tool_used(tools, "Notion")
            logs = _add_log(logs, "Notion Executor", f"Task created: '{params.get('title')}'")
            
        elif tool_name == "slack":
            res = slack_adapter.send_message(
                message=params.get("message", ""),
                channel=params.get("channel", "#alerts")
            )
            item = {"tool": "Slack", "action": "send_message", "result": res}
            actions_completed.append(item)
            notifications_sent.append(item)
            tools = _add_tool_used(tools, "Slack")
            logs = _add_log(logs, "Slack Executor", f"Notification posted to {params.get('channel')}")
            
        elif tool_name == "resend":
            res = resend_adapter.send_email(
                to_email=params.get("to", "user@company.com"),
                subject=params.get("subject", "Weather Alert"),
                html_body=params.get("body", "")
            )
            item = {"tool": "Resend", "action": "send_email", "result": res}
            actions_completed.append(item)
            notifications_sent.append(item)
            tools = _add_tool_used(tools, "Resend")
            logs = _add_log(logs, "Resend Executor", f"Email delivered to {params.get('to')}")

    return {
        "actions_completed": actions_completed,
        "actions_taken": actions_completed,
        "executed_actions": actions_completed,
        "notifications_sent": notifications_sent,
        "tools_used": tools,
        "trace_logs": logs
    }

def response_generator(state: DayGuardState) -> Dict[str, Any]:
    """Creates final user-facing response based on risk level and executed actions."""
    logger.info("Executing Node 7: response_generator")
    risk_level = state.get("risk_level", "LOW")
    actions_completed = state.get("actions_completed", state.get("executed_actions", []))
    weather = state.get("weather", state.get("weather_data", {}))
    selected = state.get("selected_tools", [])
    
    if risk_level == "HIGH":
        summary = (
            f"🚨 HIGH RISK ALERT: {weather.get('condition', 'Heavy Rain')} expected around your commute time. "
            f"Executed all required actions ({len(actions_completed)}): Created Notion preparation task, sent Slack alert, and emailed details via Resend."
        )
    elif risk_level == "MEDIUM":
        summary = (
            f"⚠️ MEDIUM RISK ADVISORY: {weather.get('condition', 'Rain')} forecast. "
            f"Created Notion preparation task and dispatched notification via your preferred channels ({', '.join(selected)})."
        )
    else:  # LOW_RISK
        summary = (
            f"☀️ LOW RISK: Weather is {weather.get('condition', 'Clear')}. No risk detected for your scheduled events today. "
            f"Skipped notifications to prevent unnecessary noise."
        )
        
    logs = _add_log(state.get("trace_logs", []), "Final Response", "Generated final summary response.")
    return {"final_response": summary, "trace_logs": logs}

# Alias mapping
planner_node = planner
context_retriever_node = context_retriever
schedule_retriever_node = gmail_checker
weather_retriever_node = weather_checker
risk_evaluator_node = decision_engine
action_planner_node = decision_engine
action_executor_node = action_executor
response_generator_node = response_generator
