from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AgentRunRequest(BaseModel):
    user_request: str = Field(
        ...,
        description="Natural language request from the user",
        example="Check my day and tell me whether the weather could affect anything important."
    )
    mock_scenario: Optional[str] = Field(
        default="rainy",
        description="Scenario to simulate ('rainy' or 'clear')"
    )

class AgentRunResponse(BaseModel):
    status: str
    user_request: str
    user_context: Optional[Dict[str, Any]] = None
    gmail_events: Optional[List[Dict[str, Any]]] = None
    weather: Optional[Dict[str, Any]] = None
    risk_level: str
    risk_reason: str
    recommended_actions: List[Dict[str, Any]] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    notifications_sent: List[Dict[str, Any]] = Field(default_factory=list)
    final_response: str
    trace_logs: List[Dict[str, Any]] = Field(default_factory=list)

class HealthCheckResponse(BaseModel):
    status: str = "ok"
    app_name: str
    environment: str
