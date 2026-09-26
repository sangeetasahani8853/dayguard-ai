---
title: DayGuard AI
emoji: 🛡️
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: true
license: mit
short_description: AI Real-World Action Agent — Weather-Aware Daily Planning with LangGraph
---

# 🛡️ DayGuard — AI Real-World Action Agent

> **Track 5 – AI Real World Agent** | Hackathon Demo

DayGuard is an autonomous AI agent that checks your calendar, email, and weather — then **decides and acts** based on real-world conditions.

## 🚀 How It Works

1. **Reads** your Gmail, Notion context, and live OpenWeather data
2. **Evaluates** risk level (HIGH / MEDIUM / LOW) using a LangGraph decision engine
3. **Conditionally acts** — creates Notion tasks, sends Slack alerts, and emails via Resend — **only when necessary**

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Agentic Workflow | LangGraph (7-node StateGraph) |
| Integrations | Swytchcode APIs (OpenWeather, Gmail, Notion, Slack, Resend) |
| UI | Streamlit |
| LLM | OpenAI GPT-4o-mini |

## 🧪 Demo Mode

The app runs in **DEMO MODE** by default — fully functional with deterministic mock data. No API keys needed to explore the full workflow.

Toggle to **LIVE MODE** to connect real Swytchcode APIs (requires environment variables).

## 📁 Project Structure

```
dayguard/
├── agent/        → LangGraph 7-node workflow (graph.py, nodes.py, router.py)
├── tools/        → Swytchcode adapters (OpenWeather, Gmail, Notion, Slack, Resend)
├── backend/      → Config & models
├── ui/           → Streamlit dashboard
└── tests/        → 29 unit & E2E tests (100% pass rate)
```

## ⚙️ Environment Variables (for Live Mode)

Set these as HF Spaces **Secrets**:

```
DEMO_MODE=false
LLM_API_KEY=...
SWYTCHCODE_API_KEY=...
OPENWEATHER_API_KEY=...
GMAIL_ACCESS_TOKEN=...
NOTION_TOKEN=...
SLACK_TOKEN=...
RESEND_API_KEY=...
```

---

Built with ❤️ for the AI Real World Agent Hackathon
