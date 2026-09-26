import logging
from dayguard.agent.state import DayGuardState

logger = logging.getLogger("DayGuard.Agent.Router")

def should_execute_actions(state: DayGuardState) -> str:
    """
    Conditional edge router function.
    Determines whether the graph should proceed to execute action tools (Notion, Slack, Resend)
    or directly generate a response without side-effects (Guardrail policy).
    """
    risk_level = state.get("risk_level", state.get("risk_assessment", {}).get("risk_level", "LOW")).upper()
    recommended_actions = state.get("recommended_actions", [])

    logger.info(f"Conditional Router evaluating state: risk_level='{risk_level}', actions_count={len(recommended_actions)}")

    if risk_level in ["HIGH", "MEDIUM"] and len(recommended_actions) > 0:
        logger.info("Routing -> action_executor (High/Medium risk detected)")
        return "action_executor"
    else:
        logger.info("Routing -> response_generator (Low risk or guardrail triggered - skipping notifications)")
        return "response_generator"
