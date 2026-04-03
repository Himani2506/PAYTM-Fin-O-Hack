import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.state import AgentState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def supervisor_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    prompt = f"""
You are a routing supervisor for a Paytm AI assistant.
Given the user input, classify it into exactly one of these 3 intents:

1. PAYMENT — user wants to send money, pay someone, transfer funds
2. PLANNER — user wants to plan a trip, book flights, book hotels, travel
3. MERCHANT — user is a merchant asking about sales, revenue, GST, business insights

User input: "{user_input}"

Reply with only one word — either PAYMENT, PLANNER, or MERCHANT.
"""

    response = llm.invoke(prompt)
    intent = response.content.strip().upper()

    if intent not in ["PAYMENT", "PLANNER", "MERCHANT"]:
        intent = "PAYMENT"

    state["intent"] = intent
    state["stream_log"] = state.get("stream_log", [])
    state["stream_log"].append(f"Supervisor routed to: {intent}")

    return state