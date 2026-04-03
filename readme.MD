# Paytm Intelligence Layer
**Agentic AI workflow for Paytm — built for Fin-O-Hack 3.0**

Paytm has 50+ features most users never find. We built an AI agent that connects all of them through a single conversation — in Hindi, English, or Hinglish.

---

## What it does

**Voice & Natural Language Payments**
"Bhaiya ko 400 bhejo" — agent resolves the contact, scores the risk, and confirms before executing.

**One-Prompt Trip Planner**
"Goa jaana hai 4 din ke liye, budget 9000 hai" — flights, hotels, budget optimization, single payment screen. No tab switching.

**Merchant Business Intelligence**
Plain-language weekly insights, GST calculation, ITC credit — delivered to merchants who never had access to this before.

**Live Thinking Stream**
Every step streams to the UI in real time — users see exactly what the agent is doing before it acts.

---

## Stack

| Layer | Tech |
|---|---|
| Mobile | Flutter |
| Backend | FastAPI + WebSockets |
| Orchestration | LangGraph |
| LLM | Gemma-3-12b-it via vLLM |
| Voice | AI4Bharat IndicConformer (ONNX) |

---

## Setup

```bash
git clone https://github.com/Himani2506/PAYTM-Fin-O-Hack
cd paytm-agent
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn langgraph langchain-groq python-dotenv websockets
```



Run:
```bash
uvicorn app.main:app --reload
```

---

## WebSocket API

Connect: `ws://localhost:8000/ws/chat`

Send:
```json
{ "input": "plan a 3 day trip to Manali for 7000 rupees" }
```

Receive:
```json
{ "type": "thinking", "message": "Searching flights to Manali..." }
{ "type": "result", "intent": "PLANNER", "workflow": {...} }
```

Confirm: `POST /confirm/{session_id}` with `{ "action": "confirm" }`

---

## Project Structure

```
app/
  main.py            — FastAPI entry point
  supervisor.py      — LLM routing agent
  pipeline.py        — LangGraph graph
  agents/
    payment_agent.py
    planner_agent.py
    merchant_agent.py
  api/
    chat.py          — WebSocket + REST
```

---

## The Gap We're Filling

640M UPI transactions happen daily — the world's largest real-time payment 
system — and there is no intelligent agent on top of it yet. That is the gap.

The global players moved first. Visa launched "Intelligent Commerce" in 2025 — 
AI agents that search, compare, and complete purchases autonomously. Mastercard 
followed with "Agent Pay" — agentic infrastructure for multi-step financial task 
execution, already in production globally. Both companies said the same thing 
publicly: by 2026, AI agents won't just assist your shopping, they will complete 
it.

India is not behind. Razorpay and NPCI piloted agentic payments on ChatGPT in 
October 2025 — users browse, order, and pay within a single chat using UPI 
Reserve Pay. It worked. But it was external, merchant-facing, and built on top 
of someone else's platform.

Nobody has built this natively inside a consumer super-app where the user 
already has their loans, travel bookings, insurance, gold, and payment history 
in one place. Paytm is the only platform in India where that cross-domain 
orchestration is even possible — 333M registered users, 12.4M Soundbox 
merchants, 15 years of transaction data across every vertical.

That is not a feature gap. That is a structural gap that only one team can fill.
---

Built by Team ByteChes
