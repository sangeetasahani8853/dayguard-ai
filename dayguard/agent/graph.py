import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from dayguard.agent.state import DayGuardState
from dayguard.agent.nodes import (
    planner,
    context_retriever,
    gmail_checker,
    weather_checker,
    decision_engine,
    action_executor,
    response_generator,
)
from dayguard.agent.router import should_execute_actions

logger = logging.getLogger("DayGuard.Agent.Graph")

def build_dayguard_graph() -> Any:
    """Build and compile the DayGuard LangGraph StateGraph workflow with 7 distinct nodes."""
    logger.info("Building DayGuard LangGraph StateGraph with 7 nodes...")
    
    workflow = StateGraph(DayGuardState)

    # Add the 7 explicit nodes
    workflow.add_node("planner", planner)
    workflow.add_node("context_retriever", context_retriever)
    workflow.add_node("gmail_checker", gmail_checker)
    workflow.add_node("weather_checker", weather_checker)
    workflow.add_node("decision_engine", decision_engine)
    workflow.add_node("action_executor", action_executor)
    workflow.add_node("response_generator", response_generator)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Connect Information Retrieval & Decision Pipeline
    workflow.add_edge("planner", "context_retriever")
    workflow.add_edge("context_retriever", "gmail_checker")
    workflow.add_edge("gmail_checker", "weather_checker")
    workflow.add_edge("weather_checker", "decision_engine")

    # Add Conditional Edge from Decision Engine to Executor or Response Generator
    workflow.add_conditional_edges(
        "decision_engine",
        should_execute_actions,
        {
            "action_executor": "action_executor",
            "response_generator": "response_generator",
        }
    )

    # Action Executor connects to Response Generator
    workflow.add_edge("action_executor", "response_generator")
    
    # Response Generator connects to END
    workflow.add_edge("response_generator", END)

    compiled_graph = workflow.compile()
    logger.info("DayGuard LangGraph StateGraph compiled successfully.")
    return compiled_graph

dayguard_agent = build_dayguard_graph()
