# DayGuard — AI Real-World Action Agent

## Hackathon Track

**Track 5 – AI Real World Agent**

### Problem Statement

Build an AI agent that can understand real-world situations using external information and take useful actions for users.

### Objective

Create an AI agent that combines real-time information with user context to provide recommendations, send updates, and automate everyday tasks.

### Required Integrations

- OpenWeather
- Gmail
- Notion
- Slack
- Resend

---

# 1. Project Overview

## DayGuard

**DayGuard is an AI-powered real-world action agent that understands a user's schedule, preferences, and real-time environmental conditions, then decides what actions should be taken.**

The MVP focuses on weather-aware daily planning.

Instead of simply answering:

> "What is the weather today?"

DayGuard answers:

> "How will today's real-world conditions affect my day, and what should I do about it?"

The agent can retrieve information, reason over multiple sources, decide which tools are required, execute actions, and provide a final outcome.

---

# 2. Example User Request

```text
Check my day and tell me whether the weather could affect anything important.
Take whatever action is necessary.
```

The agent may perform the following workflow:

```text
User Request
     ↓
Understand Intent
     ↓
Read User Context from Notion
     ↓
Read Important Events from Gmail
     ↓
Check Current/Forecast Weather
     ↓
Reason About Risk
     ↓
Decide Required Actions
     ↓
Update Notion
     ↓
Notify through Slack
     ↓
Send Email through Resend
     ↓
Verify Actions
     ↓
Final Response
```

The important point is that the agent decides which tools/actions are needed based on the situation.

---

# 3. Why This Is an AI Agent

DayGuard is not designed as a simple API dashboard.

The agent performs:

1. Understanding of a natural-language request
2. Context retrieval
3. Tool selection
4. Multi-step reasoning
5. Conditional decision-making
6. Tool execution
7. Follow-up actions
8. Final response generation

The output of one tool can influence the next tool/action.

Example:

```text
Gmail
  ↓
11:00 AM client meeting found
  ↓
Notion
  ↓
User commutes by bike
  ↓
OpenWeather
  ↓
Heavy rain expected
  ↓
Agent reasoning
  ↓
High commute risk
  ↓
Create Notion task
  ↓
Send Slack notification
  ↓
Send email
```

---

# 4. Key Use Case

## Weather-Aware Workday Assistant

DayGuard checks:

- Important meetings or events
- User preferences
- Travel/commute information
- Current weather
- Forecast information

Then it determines whether a real-world condition could affect the user's plans.

### Example

```text
Weather:
Heavy rain expected around 10:30 AM

User context:
Commutes by bike

Gmail:
11:00 AM client meeting at Gurgaon office

Agent decision:
High potential commute risk

Actions:
✓ Create preparation task in Notion
✓ Send Slack alert
✓ Send email using Resend
```

---

# 5. Example of Adaptive Agent Behavior

The agent should not blindly execute every integration.

## Scenario A — High Risk

```text
Weather: Heavy rain
Meeting: 11:00 AM
Commute: Bike
```

Agent:

```text
Risk detected.

Actions:
✓ Update Notion
✓ Send Slack notification
✓ Send email
```

## Scenario B — Low Risk

```text
Weather: Clear
Meeting: 11:00 AM
Commute: Bike
```

Agent:

```text
No significant risk detected.

Actions:
✓ Update daily plan if required
✗ Slack notification not required
✗ Email notification not required
```

This demonstrates that the AI agent makes decisions based on context rather than following a fixed API sequence.

---

# 6. Architecture

```text
                        ┌───────────────────────┐
                        │      USER PROMPT      │
                        │ "Check my day..."     │
                        └───────────┬───────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │       AI AGENT        │
                        │       LangGraph       │
                        │                       │
                        │ Understand Request    │
                        │ Reason                │
                        │ Select Tools          │
                        └───────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                │                   │                   │
                ▼                   ▼                   ▼
           ┌─────────┐         ┌─────────┐       ┌────────────┐
           │  Gmail  │         │ Notion  │       │ OpenWeather│
           │ Events  │         │ Context │       │ Real-time  │
           └────┬────┘         └────┬────┘       └─────┬──────┘
                │                   │                  │
                └───────────────────┼──────────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │   DECISION ENGINE     │
                        │                       │
                        │ Risk detected?        │
                        │ Action required?      │
                        └───────────┬───────────┘
                                    │
                       ┌────────────┼────────────┐
                       │            │            │
                       ▼            ▼            ▼
                  ┌────────┐   ┌─────────┐  ┌─────────┐
                  │ Notion │   │  Slack  │  │ Resend  │
                  │ Update │   │ Notify  │  │ Email   │
                  └────────┘   └─────────┘  └─────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   FINAL RESPONSE      │
                        └───────────────────────┘
```

---

# 7. Agent Workflow

## Step 1 — Receive User Request

Example:

```text
Check my day and tell me whether today's weather can affect anything important.
```

The agent identifies:

- Need for today's context
- Need for external real-world conditions
- Possible need for notifications/actions

---

## Step 2 — Retrieve User Context from Notion

Example Notion profile:

```text
USER PROFILE

Name: Demo User
Home: Gurgaon
Office: Gurgaon
Work Mode: Hybrid
Commute: Bike

Weather Sensitivity:
Heavy Rain = Alert

Preferred Notifications:
Slack + Email
```

The user context allows the agent to personalize the decision.

---

## Step 3 — Read Gmail

The Gmail tool searches for relevant information.

Example:

```text
Subject:
Client Meeting – 11:00 AM

Time:
11:00 AM

Location:
Gurgaon Office
```

The agent extracts the relevant event.

---

## Step 4 — Check OpenWeather

The agent retrieves:

- Current weather
- Forecast
- Rain information
- Temperature
- Wind
- Humidity
- Weather condition

Example:

```text
Condition: Heavy Rain
Expected: 10:30 AM
```

---

## Step 5 — Agent Reasoning

The agent combines the retrieved information.

Example:

```text
Meeting:
11:00 AM

Commute:
Bike

Weather:
Heavy rain around 10:30 AM

Reasoning:
The weather condition can affect the user's commute
before an important meeting.

Decision:
High risk → action required.
```

---

## Step 6 — Execute Actions

The agent decides:

### Notion

Create:

```text
Prepare for 11 AM Client Meeting

Recommended:
- Leave earlier
- Carry rain protection
- Check commute before departure
```

### Slack

Send:

```text
DayGuard Alert

Heavy rain is expected around your commute time.

Your 11:00 AM client meeting may be affected.

Recommendation:
Plan additional commute time.
```

### Resend

Send a more detailed email:

```text
Subject:
DayGuard – Weather Alert for Your 11 AM Meeting

Heavy rain is expected around your commute time.

Your 11:00 AM client meeting is scheduled at the office.

Recommended action:
Plan additional travel time and check commute conditions before leaving.

Actions taken:
✓ Notion task created
✓ Slack notification sent
```

---

# 8. LangGraph Design

A simple LangGraph can contain:

```text
START
  ↓
planner
  ↓
context_retriever
  ↓
gmail_checker
  ↓
weather_checker
  ↓
decision_engine
  ↓
conditional_router
  ├── LOW RISK → response_generator
  │
  └── HIGH RISK → action_executor
                         ↓
                       Notion
                         ↓
                       Slack
                         ↓
                       Resend
                         ↓
                   response_generator
                         ↓
                        END
```

---

# 9. Suggested Agent State

```python
state = {
    "user_request": "",
    "user_context": {},
    "gmail_events": [],
    "weather": {},
    "risk_level": "",
    "recommended_actions": [],
    "tools_used": [],
    "notifications_sent": []
}
```

Each node can update the shared state.

---

# 10. Tool Definitions

Suggested tool abstractions:

```python
get_weather(location)

get_gmail_events(query)

get_notion_user_context()

create_notion_task(task)

send_slack_message(message)

send_email(to, subject, body)
```

The LLM/agent should decide which tools to call.

Do not hard-code every tool call into a single linear workflow.

---

# 11. Suggested Project Structure

```text
dayguard/
│
├── app.py
│
├── agent/
│   ├── graph.py
│   ├── state.py
│   └── prompts.py
│
├── tools/
│   ├── gmail.py
│   ├── weather.py
│   ├── notion.py
│   ├── slack.py
│   └── resend.py
│
├── config/
│   └── settings.py
│
├── requirements.txt
│
├── README.md
│
└── .env.example
```

---

# 12. Recommended Technology Stack

```text
Frontend:
Streamlit or React

Backend:
Python + FastAPI

Agent Framework:
LangGraph

LLM:
Groq / another compatible LLM

Integrations:
Swytchcode APIs

Storage:
Simple JSON / SQLite / LangGraph state

Deployment:
Docker or any suitable deployment platform
```

---

# 13. Demo UI

The UI should make the agent behavior visible.

Example:

```text
┌─────────────────────────────────────────────┐
│                DAYGUARD AI                  │
├─────────────────────────────────────────────┤
│ User Prompt                                  │
│                                              │
│ Check my day and tell me what I need to do  │
│ based on today's conditions.                 │
├─────────────────────────────────────────────┤
│ Agent Workflow                               │
│                                              │
│ ✓ Understanding request                     │
│ ✓ Reading user context                      │
│ ✓ Checking Gmail                            │
│ ✓ Checking weather                          │
│ ✓ Evaluating risk                           │
│ ✓ Creating Notion task                      │
│ ✓ Sending Slack notification                │
│ ✓ Sending email                             │
├─────────────────────────────────────────────┤
│ Final Result                                 │
│                                              │
│ Heavy rain is expected before your 11 AM     │
│ meeting. I created a preparation task and    │
│ notified you through Slack and email.        │
└─────────────────────────────────────────────┘
```

---

# 14. Important Demo Scenario

Use a single strong end-to-end demo.

## Prompt

```text
Check my day and take whatever action is necessary based on today's conditions.
```

## Expected execution

```text
1. Agent understands request
2. Read Gmail
3. Find important meeting
4. Read Notion profile
5. Check OpenWeather
6. Compare weather with event and user context
7. Decide risk
8. Create Notion task
9. Send Slack notification
10. Send Resend email
11. Return final summary
```

---

# 15. Second Demo Scenario

Change the weather to a safe condition.

```text
Weather:
Clear
```

Expected:

```text
No important risk detected.

Notion:
Optional daily plan update

Slack:
No message

Resend:
No email
```

This demonstrates adaptive decision-making.

---

# 16. Future Scope

The MVP should be positioned as a weather-aware daily assistant, but the architecture can evolve into a broader:

# Personal Real-World Action Agent

Potential extensions:

## Travel Assistant

```text
Gmail
  ↓
Find travel reservation
  ↓
OpenWeather
  ↓
Check destination conditions
  ↓
Notion
  ↓
Create preparation checklist
  ↓
Slack / Email
  ↓
Notify user
```

## Emergency Preparedness

The agent could combine real-world conditions with the user's stored context and trigger preparedness workflows.

## Workday Assistant

The agent could understand:

- Meetings
- Appointments
- Deadlines
- Travel
- Environmental conditions

and proactively create an actionable daily plan.

## Location-Aware Personal Assistant

The same agent architecture could eventually support context-aware assistance based on location, schedule, preferences, and external information.

## Enterprise Employee Assistant

The system could help organizations provide contextual alerts and action workflows for employees during weather or other real-world disruptions.

---

# 17. Product Vision

The long-term vision is:

```text
                 PERSONAL REAL-WORLD AGENT
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Weather          Travel             Work
          │                │                │
          ▼                ▼                ▼
      Conditions        Booking          Meetings
      Forecasts         Changes           Tasks
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    AI REASONING
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Notion        Slack        Email
```

The key product idea is:

> **The agent does not just tell the user what is happening. It understands what it means for the user and takes the next useful action.**

---

# 18. Why This Fits the Hackathon

The project is designed around the hackathon's agent requirements:

- Natural-language user request
- Agent reasoning
- Tool selection
- Multiple API calls
- Intermediate result analysis
- Conditional next actions
- Final useful outcome
- Meaningful use of at least 3 Swytchcode APIs

Recommended API usage:

```text
OpenWeather → Real-world information
Gmail       → User schedule/context
Notion      → User profile + action management
Slack       → Instant notification
Resend      → Detailed email notification
```

Using all five integrations strengthens the multi-tool workflow.

---

# 19. Judging Strategy

Focus development effort on:

## API Integration

Make all integrations meaningful.

## Technical Implementation

Use an actual agent framework and clear state/conditional routing.

## Innovation

Show that the agent connects real-world conditions with personal context and takes action.

## Functionality

The entire workflow should work end-to-end.

## Real-World Impact

Explain how the architecture can extend into travel, emergency preparedness, workday planning, and enterprise assistance.

## UX & Presentation

Make the agent's actions and decisions visible in the UI.

---

# 20. Guardrails

Do not let the agent send every notification every time.

Example rules:

```text
Slack:
Only for important work-related alerts.

Email:
Only when a meaningful notification is required.

Notion:
Create a task only when user action is necessary.
```

The agent should avoid unnecessary actions.

---

# 21. Observability

Display an execution log such as:

```text
10:21:03
Received user request

10:21:04
Selected Gmail tool

10:21:04
Important meeting found

10:21:05
Selected Notion tool

10:21:05
User commute preference found

10:21:06
Selected OpenWeather

10:21:07
High weather risk detected

10:21:07
Selected Notion + Slack + Resend

10:21:09
Actions completed
```

This helps judges understand that the system is reasoning and executing rather than simply displaying a fixed response.

---

# 22. Final Demo Script

## Problem

> People don't have time to continuously check weather, emails, schedules, and notifications to understand how real-world conditions affect their day.

## Solution

> DayGuard is an AI agent that combines real-time environmental information with personal context and takes useful actions automatically.

## Demo

Prompt:

```text
Check my day and take whatever action is necessary based on today's conditions.
```

Agent flow:

```text
Gmail
→ Important meeting found

Notion
→ User context found

OpenWeather
→ Heavy rain detected

Agent
→ High-risk situation

Notion
→ Preparation task created

Slack
→ Alert sent

Resend
→ Email sent
```

## Closing

> DayGuard doesn't just tell users what's happening. It understands what it means for them and takes the next useful action.

---

# 23. Submission Checklist

```text
[ ] Working AI agent
[ ] Agentic framework
[ ] Minimum 3 Swytchcode APIs
[ ] Recommended: all 5 Track 5 APIs
[ ] Natural-language prompt interface
[ ] Tool selection
[ ] Multi-step workflow
[ ] Conditional decisions
[ ] Real API results
[ ] Final response
[ ] Public GitHub repository
[ ] README
[ ] Architecture diagram
[ ] Setup instructions
[ ] Working demo/prototype
[ ] Commudle submission
[ ] Test/dummy data where appropriate
```

---

# 24. One-Line Pitch

> **DayGuard is an AI real-world action agent that understands your schedule, your preferences, and what's happening around you—then decides and executes the next useful action.**

