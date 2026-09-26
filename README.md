# DayGuard — AI Real-World Action Agent

> **One-Line Pitch:** DayGuard is an AI real-world action agent that understands your schedule, your preferences, and what's happening around you—then decides and executes the next useful action.

---

## Hackathon Track
**Track 5 – AI Real World Agent**

### Problem Statement
People don't have time to continuously check weather forecasts, emails, calendar schedules, and notifications to understand how changing real-world conditions affect their day.

### Solution
Instead of simply answering *"What is the weather today?"*, **DayGuard** answers:
> *"How will today's real-world conditions affect my day, and what should I do about it?"*

DayGuard is a weather-aware daily planning AI agent built with **LangGraph**, **FastAPI**, **Streamlit**, and 5 **Swytchcode API Adapters** (**OpenWeather**, **Gmail**, **Notion**, **Slack**, **Resend**).

---

## Architecture Diagram

```text
                        ┌───────────────────────────────────┐
                        │       Streamlit Frontend UI       │
                        │  - Natural Language Input         │
                        │  - Live Execution Trace Timeline  │
                        │  - Risk Level & Decision Cards    │
                        └─────────────────┬─────────────────┘
                                          │
                                          ▼
                        ┌───────────────────────────────────┐
                        │   LangGraph Agent Orchestrator    │
                        │  - DayGuardState Engine           │
                        │  - Dynamic Planner & Router       │
                        └─────────────────┬─────────────────┘
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         │                                │                                │
         ▼                                ▼                                ▼
┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
│ Notion Adapter  │              │  Gmail Adapter  │              │OpenWeather Adapt│
│ User Context &  │              │ Fetch Calendar  │              │  Get Forecast   │
│ Preferences     │              │ Meetings        │              │  Conditions     │
└────────┬────────┘              └────────┬────────┘              └────────┬────────┘
         │                                │                                │
         └────────────────────────────────┼────────────────────────────────┘
                                          │
                                          ▼
                        ┌───────────────────────────────────┐
                        │     Decision Engine & Risk        │
                        │  - Evaluate Risk Level            │
                        │  - Select Required Action Tools   │
                        └─────────────────┬─────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │ (HIGH / MEDIUM Risk)                        │ (LOW Risk - Skip)
                   ▼                                             ▼
┌───────────────────────────────────┐           ┌───────────────────────────────────┐
│      Action Execution Layer       │           │        Response Generator         │
│  - Notion: Create Prep Task       │──────────►│  - Formulate Final Summary        │
│  - Slack: Send Channel Alert      │           │    Response for User              │
│  - Resend: Deliver Email Notice   │           └───────────────────────────────────┘
└───────────────────────────────────┘
```

---

## 7 LangGraph Nodes & Execution Pipeline

```text
1. planner            ──► Parses query & formulates information gathering strategy
2. context_retriever  ──► Retrieves user commute mode (Bike) & location from Notion
3. gmail_checker      ──► Fetches scheduled 11:00 AM Client Strategy Meeting from Gmail
4. weather_checker    ──► Fetches real-time forecast (Heavy Rain / 90% rain prob) from OpenWeather
5. decision_engine    ──► Combines data & computes Risk Level (HIGH / MEDIUM / LOW)
6. action_executor   ──► Conditionally executes Notion task, Slack alert, Resend email
7. response_generator ──► Formulates concise summary response for user
```

---

## Risk Policy & Conditional Routing Rules

| Risk Level | Weather / Schedule Condition | Selected Tools (`selected_tools`) | Skipped Tools (`skipped_tools`) | Actions Completed |
| :--- | :--- | :--- | :--- | :--- |
| **`HIGH_RISK`** | Heavy rain near commute time before important meeting | `["notion", "slack", "resend"]` | `[]` | Notion prep task + Slack alert + Resend email delivered. |
| **`MEDIUM_RISK`** | Moderate rain / weather advisory | `["notion"]` + preferred channels | Non-preferred channels | Notion task + notification per user preference. |
| **`LOW_RISK`** | Clear skies / normal conditions | `[]` *(None)* | `["notion", "slack", "resend"]` | **Zero notifications sent** (prevents notification noise). |

---

## Project Structure

```text
dayguard/
├── app.py                      # FastAPI runner script
├── backend/
│   ├── config.py               # Pydantic Settings, secret masking & log redaction
│   ├── main.py                 # FastAPI application routes (/health, /api/agent/run)
│   └── models.py               # Request & Response Pydantic models
├── agent/
│   ├── state.py                # Strongly-typed DayGuardState schema & sanitization
│   ├── prompts.py              # System prompts for agent reasoning
│   ├── router.py               # Conditional risk routing logic
│   ├── nodes.py                # 7 LangGraph node functions
│   └── graph.py                # Compiled LangGraph StateGraph engine
├── tools/
│   ├── base.py                 # SwytchcodeBaseAdapter HTTP client & exceptions
│   ├── gmail.py                # GmailAdapter (calendar event search)
│   ├── weather.py              # OpenWeatherAdapter (forecast & weather severity)
│   ├── notion.py               # NotionAdapter (profile context & task creation)
│   ├── slack.py                # SlackAdapter (instant notification dispatch)
│   ├── resend.py               # ResendAdapter (HTML transactional email)
│   └── INTEGRATIONS_STATUS.md  # API documentation & credentials audit
├── ui/
│   └── streamlit_app.py        # Streamlit demo dashboard with workflow trace
├── tests/
│   ├── test_adapters.py        # Unit tests for all 5 tool adapters
│   ├── test_agent.py           # Unit tests for graph state machine
│   ├── test_config.py          # Unit tests for config security & log redaction
│   ├── test_demo_mode.py       # Unit tests for DEMO MODE vs LIVE MODE
│   ├── test_router.py          # Unit tests for risk-based routing
│   └── test_e2e.py             # Exhaustive end-to-end test suite
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
└── .gitignore                  # Exclusion list for secrets and virtual environments
```

---

## Setup & Installation Instructions

### 1. Prerequisites
- Python 3.10+
- Virtual environment (`venv`)

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/dayguard.git
cd dayguard

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to set your credentials or leave `DEMO_MODE=true` for deterministic hackathon demonstration:
```env
DEMO_MODE=true
OPENAI_API_KEY=your_openai_key
SWYTCHCODE_API_KEY=your_swytchcode_key
```

### 4. Running the Application

#### Option A: Streamlit Demo Dashboard (Recommended)
```bash
streamlit run dayguard/ui/streamlit_app.py
```

#### Option B: FastAPI Backend API Server
```bash
python dayguard/app.py
```
FastAPI interactive docs will be available at `http://localhost:8000/docs`.

---

## Running the Verification Test Suite

Run the full pytest suite (29 tests):
```bash
set PYTHONPATH=. && dayguard\.venv\Scripts\python.exe -m pytest dayguard/tests/ -v
```

---

## Hackathon Submission Verification Checklist

- [x] **Real AI Agent**: Dynamic reasoning and tool selection, not a fixed API script.
- [x] **LangGraph Orchestration**: Compiled 7-node state machine workflow.
- [x] **Minimum 3 Swytchcode APIs**: Integrates all 5 Track 5 APIs (OpenWeather, Gmail, Notion, Slack, Resend).
- [x] **OpenWeather**: Real-time forecast & rain probability metrics.
- [x] **Gmail**: Calendar event search for scheduled client meetings.
- [x] **Notion**: Profile context retrieval (commute mode) & task page creation.
- [x] **Slack**: Instant notification alert dispatch.
- [x] **Resend**: Transactional email advisory delivery.
- [x] **Natural-Language Prompt**: Interactive text box input.
- [x] **Agent Tool Selection**: Dynamic `selected_tools` vs `skipped_tools` tracking.
- [x] **Multi-Step Workflow**: Planner $\rightarrow$ Context $\rightarrow$ Schedule $\rightarrow$ Weather $\rightarrow$ Decision $\rightarrow$ Executor $\rightarrow$ Summary.
- [x] **Conditional Decisions**: Risk policy branches execution dynamically.
- [x] **Intermediate Results Influence Next Actions**: Gmail schedule + Notion commute mode + OpenWeather forecast drive risk level and tool selection.
- [x] **Working End-to-End Demo**: Streamlit dashboard with workflow trace checklist.
- [x] **README**: Comprehensive documentation file.
- [x] **Architecture Diagram**: Formatted ASCII system architecture diagram.
- [x] **Setup Instructions**: Virtual environment & execution commands.
- [x] **.env.example**: Template for environment variables.
- [x] **.gitignore**: Excludes `.env`, `.venv`, and sensitive credential files.
- [x] **Tests**: 29 passed unit and end-to-end tests.
