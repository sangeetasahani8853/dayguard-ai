import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dayguard.backend.config import settings, logger
from dayguard.backend.models import AgentRunRequest, AgentRunResponse, HealthCheckResponse
from dayguard.agent.graph import dayguard_agent
from dayguard.agent.state import sanitize_state_for_ui

app = FastAPI(
    title=settings.app_name,
    description="DayGuard AI Real-World Action Agent Backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    return HealthCheckResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment
    )

@app.post("/api/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest):
    """Execute the DayGuard AI agent with natural language input."""
    logger.info(f"Received agent run request: '{request.user_request}' (Scenario: {request.mock_scenario})")
    try:
        initial_state = {
            "user_request": request.user_request,
            "mock_scenario": request.mock_scenario or "rainy",
            "plan": [],
            "user_context": {},
            "gmail_events": [],
            "weather": {},
            "weather_data": {},
            "risk_level": "LOW",
            "risk_reason": "",
            "risk_assessment": {},
            "recommended_actions": [],
            "tools_used": [],
            "actions_taken": [],
            "executed_actions": [],
            "notifications_sent": [],
            "trace_logs": [],
            "final_response": "",
        }

        # Invoke compiled LangGraph agent
        final_state = dayguard_agent.invoke(initial_state)
        safe_state = sanitize_state_for_ui(final_state)

        return AgentRunResponse(
            status="completed",
            user_request=safe_state.get("user_request", ""),
            user_context=safe_state.get("user_context"),
            gmail_events=safe_state.get("gmail_events"),
            weather=safe_state.get("weather", safe_state.get("weather_data")),
            risk_level=safe_state.get("risk_level", "LOW"),
            risk_reason=safe_state.get("risk_reason", ""),
            recommended_actions=safe_state.get("recommended_actions", []),
            tools_used=safe_state.get("tools_used", []),
            actions_taken=safe_state.get("actions_taken", safe_state.get("executed_actions", [])),
            notifications_sent=safe_state.get("notifications_sent", []),
            final_response=safe_state.get("final_response", ""),
            trace_logs=safe_state.get("trace_logs", []),
        )
    except Exception as e:
        logger.error(f"Error executing DayGuard agent graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
