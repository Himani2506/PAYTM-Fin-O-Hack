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
| LLM | Llama 3.3 70B via Groq |
| Voice | Whisper-Hindi2Hinglish-Apex |

---

## Setup

```bash
git clone https://github.com/yourusername/paytm-agent
cd paytm-agent
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn langgraph langchain-groq python-dotenv websockets
```

Add to `.env`:
```
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
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

640M UPI transactions happen daily — the world's largest real-time payment system — with no intelligent agent on top. Visa and Mastercard launched agentic payment layers in 2025. Razorpay proved agentic UPI works on ChatGPT. Nobody has built it natively inside India's most comprehensive payment platform — until now.

---

Built by Team ByteChes
