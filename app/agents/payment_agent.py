import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.state import AgentState
import json

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def payment_agent(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    extraction_prompt = f"""
You are a payment assistant for Paytm, India's leading payment app.
Extract payment details from this input: "{user_input}"

The input may be in Hindi, English, or Hinglish (mix of both).
Examples:
- "pay 500 to Raj" → payee: Raj, amount: 500
- "bhaiya ko 400 bhejo" → payee: Bhaiya, amount: 400
- "send 1000 rupees to Priya" → payee: Priya, amount: 1000
- "Sharma ji ko paanch sau do" → payee: Sharma Ji, amount: 500

Return ONLY a JSON object with these fields:
{{
    "payee": "name of person to pay",
    "amount": number,
    "note": "reason for payment if mentioned, else null"
}}
"""

    response = llm.invoke(extraction_prompt)
    
    try:
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        details = json.loads(content)
    except:
        details = {"payee": "Unknown", "amount": 0, "note": None}

    payee = details.get("payee", "Unknown")
    amount = details.get("amount", 0)
    note = details.get("note")

    risk_score = 0.1
    if amount > 10000:
        risk_score = 0.8
    elif amount > 5000:
        risk_score = 0.5

    risk_reason = None
    if risk_score > 0.5:
        risk_reason = f"High value transaction of ₹{amount} — please verify recipient"
    elif risk_score > 0.3:
        risk_reason = f"Medium value transaction — confirm before proceeding"

    state["risk_score"] = risk_score
    state["drafted_workflow"] = {
        "action": "P2P_TRANSFER",
        "payee": payee,
        "upi_id": f"{payee.lower().replace(' ', '')}@paytm",
        "amount": amount,
        "note": note,
        "risk_score": risk_score,
        "risk_reason": risk_reason
    }
    state["execution_status"] = "pending_confirmation"
    state["stream_log"].append(f"Payment parsed: ₹{amount} to {payee}")
    state["stream_log"].append(f"Risk assessment: {'High' if risk_score > 0.5 else 'Medium' if risk_score > 0.3 else 'Low'} ({risk_score})")
    if risk_reason:
        state["stream_log"].append(f"Warning: {risk_reason}")

    return state