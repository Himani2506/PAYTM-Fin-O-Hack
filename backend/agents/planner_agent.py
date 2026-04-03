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

MOCK_FLIGHTS = {
    "default": {"price_per_km": 3.5, "base_price": 1500},
    "Manali": {"price": 2500, "duration": "1h 20m"},
    "Goa": {"price": 3200, "duration": "2h 10m"},
    "Jaipur": {"price": 1800, "duration": "1h"},
    "Mumbai": {"price": 2800, "duration": "2h"},
    "Shimla": {"price": 2200, "duration": "1h 10m"},
    "Udaipur": {"price": 2000, "duration": "1h 30m"},
    "Rishikesh": {"price": 1900, "duration": "1h"},
    "Ladakh": {"price": 4500, "duration": "2h 30m"},
    "Kerala": {"price": 3800, "duration": "2h 45m"},
}

MOCK_HOTELS = {
    "default": {"price_per_night": 1500},
    "Manali": {"name": "Snow Peak Inn", "price_per_night": 1200},
    "Goa": {"name": "Beach Breeze Resort", "price_per_night": 1800},
    "Jaipur": {"name": "Royal Heritage Stay", "price_per_night": 1500},
    "Mumbai": {"name": "City Central Hotel", "price_per_night": 2200},
    "Shimla": {"name": "Hill View Lodge", "price_per_night": 1100},
    "Udaipur": {"name": "Lake Palace Inn", "price_per_night": 1700},
    "Rishikesh": {"name": "Ganga View Hostel", "price_per_night": 800},
    "Ladakh": {"name": "Mountain Camp", "price_per_night": 1400},
    "Kerala": {"name": "Backwater Retreat", "price_per_night": 2000},
}

def planner_agent(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    extraction_prompt = f"""
You are a travel planning assistant for Paytm in India.
Extract trip details from this input: "{user_input}"

The input may be in Hindi, English, or Hinglish.
Examples:
- "plan a 3 day trip to Manali for 7000 rupees" → destination: Manali, days: 3, budget: 7000
- "Goa jaana hai 5 din ke liye, budget 10000 hai" → destination: Goa, days: 5, budget: 10000
- "weekend trip to Shimla under 5k" → destination: Shimla, days: 2, budget: 5000

Return ONLY a JSON object:
{{
    "destination": "city name",
    "days": number,
    "budget": number,
    "travelers": number (default 1 if not mentioned),
    "preferences": "any special preferences mentioned, else null"
}}
"""

    response = llm.invoke(extraction_prompt)

    try:
        content = response.content.strip()
        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()
        details = json.loads(content)
    except:
        details = {"destination": "Manali", "days": 3, "budget": 5000, "travelers": 1, "preferences": None}

    destination = details.get("destination", "Manali")
    days = details.get("days", 3)
    budget = details.get("budget", 5000)
    travelers = details.get("travelers", 1)
    preferences = details.get("preferences")

    state["stream_log"].append(f"Parsed trip: {days} days to {destination} for ₹{budget}")
    state["stream_log"].append(f"Searching flights to {destination}...")

    flight = MOCK_FLIGHTS.get(destination, {"price": MOCK_FLIGHTS["default"]["base_price"], "duration": "2h"})
    flight_total = flight["price"] * travelers

    state["stream_log"].append(f"Found flight at ₹{flight['price']} per person")
    state["stream_log"].append(f"Searching hotels in {destination}...")

    hotel = MOCK_HOTELS.get(destination, {"name": f"{destination} Hotel", "price_per_night": MOCK_HOTELS["default"]["price_per_night"]})
    remaining_budget = budget - flight_total
    max_nights = remaining_budget // hotel["price_per_night"]
    actual_days = min(days, max_nights)
    hotel_total = hotel["price_per_night"] * actual_days
    total_cost = flight_total + hotel_total
    daily_expenses = (budget - total_cost) // actual_days if actual_days > 0 else 0

    state["stream_log"].append(f"Found {hotel.get('name', 'hotel')} at ₹{hotel['price_per_night']}/night")
    state["stream_log"].append(f"Optimizing budget: ₹{total_cost} total, ₹{daily_expenses}/day for food & activities")

    insight_prompt = f"""
You are a travel advisor. Give a 2 sentence travel tip for someone visiting {destination} for {actual_days} days with ₹{daily_expenses} per day for food and activities. Be specific and practical. No fluff.
"""
    insight_response = llm.invoke(insight_prompt)
    travel_tip = insight_response.content.strip()

    state["drafted_workflow"] = {
        "action": "TRIP_PLAN",
        "destination": destination,
        "days": actual_days,
        "travelers": travelers,
        "preferences": preferences,
        "flight": {
            "to": destination,
            "price_per_person": flight["price"],
            "total": flight_total,
            "duration": flight.get("duration", "2h")
        },
        "hotel": {
            "name": hotel.get("name", f"{destination} Hotel"),
            "price_per_night": hotel["price_per_night"],
            "total": hotel_total
        },
        "daily_budget": daily_expenses,
        "total_cost": total_cost,
        "original_budget": budget,
        "savings": budget - total_cost,
        "travel_tip": travel_tip
    }
    state["execution_status"] = "pending_confirmation"
    state["stream_log"].append(f"Trip ready: {actual_days} days to {destination} | Total ₹{total_cost} | Saves ₹{budget - total_cost}")

    return state