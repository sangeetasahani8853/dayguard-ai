"""
DayGuard AI — Hugging Face Spaces Entry Point
Streamlit app_file: this file is loaded directly by HF Spaces.
"""
import sys
import os

# Ensure repo root is on sys.path so 'dayguard' package resolves correctly
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

# Force DEMO_MODE=true by default on HF Spaces (no secrets required to explore)
if "DEMO_MODE" not in os.environ:
    os.environ["DEMO_MODE"] = "true"

# ── Run the Streamlit UI ──────────────────────────────────────────────────────
import streamlit as st
from dayguard.backend.config import settings
from dayguard.agent.graph import dayguard_agent
from dayguard.agent.state import sanitize_state_for_ui

# 1. Page Config
st.set_page_config(
    page_title="DayGuard — AI Real-World Action Agent",
    page_icon="🛡️",
    layout="wide"
)

# 2. Header
st.title("🛡️ DayGuard — AI Real-World Action Agent")
st.caption("Track 5 – AI Real World Agent | Weather-Aware Daily Planning & Action Engine")

col_header_left, col_header_right = st.columns([3, 1])

with col_header_right:
    active_demo_mode = st.toggle("Enable DEMO MODE", value=True)
    if active_demo_mode:
        st.markdown("### 🧪 `DEMO MODE` (Active)")
        st.caption("Using deterministic hackathon demo data & mock adapters")
    else:
        st.markdown("### ⚡ `LIVE MODE` (Active)")
        st.caption("Connecting to live Swytchcode API endpoints")

st.markdown("---")

# 3. Input
col_input, col_preset = st.columns([2, 1])

with col_input:
    user_prompt = st.text_area(
        "Natural-Language Request",
        value="Check my day and tell me whether the weather could affect anything important. Take whatever action is necessary.",
        height=100,
        help="Enter any natural language instruction for DayGuard."
    )

with col_preset:
    scenario = st.radio(
        "Demo Testing Scenario",
        options=["rainy", "medium", "clear"],
        format_func=lambda x: {
            "rainy": "🌧️ Heavy Rain (HIGH RISK)",
            "medium": "🌦️ Moderate Rain (MEDIUM RISK)",
            "clear": "☀️ Clear Weather (LOW RISK)"
        }[x],
        index=0
    )

# 4. Run Button
run_btn = st.button("🚀 Run Agent", type="primary", use_container_width=True)

if run_btn:
    mode_banner = "DEMO MODE" if active_demo_mode else "LIVE MODE"
    with st.spinner(f"Agent running in **{mode_banner}**..."):
        try:
            initial_state = {
                "user_request": user_prompt,
                "mock_scenario": scenario,
                "demo_mode": active_demo_mode,
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

            raw_result = dayguard_agent.invoke(initial_state)
            st.session_state["agent_result"] = sanitize_state_for_ui(raw_result)
            st.success(f"Agent execution complete in **{mode_banner}**!")
        except Exception as e:
            st.error(f"Error executing agent graph: {e}")

# 5. Results
if "agent_result" in st.session_state:
    res = st.session_state["agent_result"]
    risk_level = res.get("risk_level", "LOW")
    reason = res.get("reason", res.get("risk_reason", ""))
    selected_tools = res.get("selected_tools", [])
    skipped_tools = res.get("skipped_tools", [])
    actions_completed = res.get("actions_completed", res.get("executed_actions", []))
    final_response = res.get("final_response", "")
    run_demo_mode = res.get("demo_mode", True)

    st.markdown("---")

    if run_demo_mode:
        st.info("ℹ️ Execution Provider: **DEMO MODE** (Deterministic Hackathon Mock Data)")
    else:
        st.info("⚡ Execution Provider: **LIVE MODE** (Swytchcode API Gateways)")

    col_risk, col_reason = st.columns([1, 2])
    with col_risk:
        if risk_level == "HIGH":
            st.error("### 🚨 Risk Level: HIGH")
        elif risk_level == "MEDIUM":
            st.warning("### ⚠️ Risk Level: MEDIUM")
        else:
            st.success("### ☀️ Risk Level: LOW")

    with col_reason:
        st.markdown("**Decision Reason:**")
        st.info(reason)

    st.markdown("### 💬 Final Response")
    st.success(final_response)

    st.markdown("---")

    col_left_panel, col_right_panel = st.columns([1, 1])

    with col_left_panel:
        st.subheader("Agent Workflow Status")
        st.markdown("```text")
        st.text("✓ Understanding request")

        if res.get("user_context"):
            st.text("✓ Reading Notion context")
        else:
            st.text("✗ Reading Notion context")

        if res.get("gmail_events"):
            st.text("✓ Checking Gmail")
        else:
            st.text("✗ Checking Gmail")

        if res.get("weather"):
            st.text("✓ Checking weather")
        else:
            st.text("✗ Checking weather")

        st.text(f"✓ Evaluating risk ({risk_level})")

        if "notion" in selected_tools:
            st.text("✓ Creating Notion task")
        else:
            st.text("✗ Notion task (skipped)")

        if "slack" in selected_tools:
            st.text("✓ Sending Slack notification")
        else:
            st.text("✗ Slack notification (skipped)")

        if "resend" in selected_tools:
            st.text("✓ Sending email via Resend")
        else:
            st.text("✗ Email via Resend (skipped)")
        st.markdown("```")

        st.subheader("Tool Selection Breakdown")
        st.markdown("**Selected Tools:** " + (", ".join([f"`{t}`" for t in selected_tools]) if selected_tools else "*None (Low risk)*"))
        st.markdown("**Skipped Tools:** " + (", ".join([f"`{t}`" for t in skipped_tools]) if skipped_tools else "*None*"))

        with st.expander("Detailed Log Timeline"):
            for log in res.get("trace_logs", []):
                st.write(f"**[{log.get('timestamp')}] {log.get('step')}**: {log.get('message')}")

    with col_right_panel:
        st.subheader("Actions Completed")
        if actions_completed:
            for act in actions_completed:
                st.write(f"✓ **{act.get('tool')} Tool** (`{act.get('action')}`)")
                st.json(act.get("result"))
        else:
            st.info("No action tools were executed (LOW_RISK policy guardrail skipped notifications).")

    st.markdown("---")
    st.subheader("API Results & Information Gathered")
    tab_notion, tab_gmail, tab_weather = st.tabs(["Notion Context", "Gmail Events", "OpenWeather Forecast"])

    with tab_notion:
        st.json(res.get("user_context", {}))

    with tab_gmail:
        st.json(res.get("gmail_events", []))

    with tab_weather:
        st.json(res.get("weather", res.get("weather_data", {})))
