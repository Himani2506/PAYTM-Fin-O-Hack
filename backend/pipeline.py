from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.state import AgentState
from app.supervisor import supervisor_node
from app.agents.payment_agent import payment_agent
from app.agents.planner_agent import planner_agent
from app.agents.merchant_agent import merchant_agent
from app.agents.hitl_node import hitl_node

def route_intent(state: AgentState) -> str:
    return state["intent"]

def build_pipeline():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("payment", payment_agent)
    graph.add_node("planner", planner_agent)
    graph.add_node("merchant", merchant_agent)
    graph.add_node("hitl", hitl_node)          # Phase 4 HITL checkpoint

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_intent,
        {
            "PAYMENT": "payment",
            "PLANNER": "planner",
            "MERCHANT": "merchant"
        }
    )

    # PAYMENT + PLANNER go through HITL; MERCHANT streams directly to END
    graph.add_edge("payment",  "hitl")
    graph.add_edge("planner",  "hitl")
    graph.add_edge("merchant", END)
    graph.add_edge("hitl",     END)

    # MemorySaver lets LangGraph persist state across .invoke() calls
    # so we can resume after the interrupt
    checkpointer = MemorySaver()
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["hitl"],   # pause BEFORE hitl runs
    )

pipeline = build_pipeline()