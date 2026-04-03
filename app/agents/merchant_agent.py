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

MOCK_TRANSACTIONS = [
    {"day": "Monday", "revenue": 4200, "orders": 18, "top_item": "Chai"},
    {"day": "Tuesday", "revenue": 3800, "orders": 15, "top_item": "Samosa"},
    {"day": "Wednesday", "revenue": 5100, "orders": 22, "top_item": "Chai"},
    {"day": "Thursday", "revenue": 4700, "orders": 19, "top_item": "Lunch Thali"},
    {"day": "Friday", "revenue": 6200, "orders": 27, "top_item": "Lunch Thali"},
    {"day": "Saturday", "revenue": 7100, "orders": 31, "top_item": "Special Thali"},
    {"day": "Sunday", "revenue": 2900, "orders": 11, "top_item": "Chai"},
]

def merchant_agent(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    total_revenue = sum(d["revenue"] for d in MOCK_TRANSACTIONS)
    total_orders = sum(d["orders"] for d in MOCK_TRANSACTIONS)
    best_day = max(MOCK_TRANSACTIONS, key=lambda x: x["revenue"])
    worst_day = min(MOCK_TRANSACTIONS, key=lambda x: x["revenue"])
    avg_order_value = total_revenue // total_orders
    gst_payable = round(total_revenue * 0.18, 2)
    itc_credit = round(gst_payable * 0.3, 2)
    net_gst = round(gst_payable - itc_credit, 2)

    state["stream_log"].append("Fetching your transaction history...")
    state["stream_log"].append(f"Analysing {total_orders} orders across 7 days...")
    state["stream_log"].append("Calculating GST liability and ITC credit...")
    state["stream_log"].append("Generating business insights...")

    insight_prompt = f"""
You are a business analyst for a small Indian merchant using Paytm Soundbox.
The merchant asked: "{user_input}"

Here is their weekly data:
- Total Revenue: ₹{total_revenue}
- Total Orders: {total_orders}
- Average Order Value: ₹{avg_order_value}
- Best Day: {best_day['day']} with ₹{best_day['revenue']} and {best_day['orders']} orders
- Worst Day: {worst_day['day']} with ₹{worst_day['revenue']} and {worst_day['orders']} orders
- Top selling item: {best_day['top_item']}
- GST Due: ₹{net_gst} after ITC credit of ₹{itc_credit}
- Daily breakdown: {json.dumps(MOCK_TRANSACTIONS)}

Give 3 sharp, actionable business insights in plain simple English (no bullet symbols, just numbered 1. 2. 3.).
Be specific with the numbers. Sound like a smart friend giving advice, not a corporate report.
Keep it under 100 words total.
"""

    response = llm.invoke(insight_prompt)
    insights = response.content.strip()

    state["drafted_workflow"] = {
        "action": "MERCHANT_INSIGHTS",
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "best_day": best_day,
        "worst_day": worst_day,
        "gst_payable": gst_payable,
        "itc_credit": itc_credit,
        "net_gst": net_gst,
        "insights": insights,
        "weekly_data": MOCK_TRANSACTIONS
    }
    state["execution_status"] = "completed"
    state["stream_log"].append(f"Analysis complete | Revenue ₹{total_revenue} | GST due ₹{net_gst}")

    return state