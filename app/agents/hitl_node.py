from datetime import datetime, timezone
from app.state import AgentState


def hitl_node(state: AgentState) -> AgentState:
    """
    Phase 4 — Human-in-the-Loop checkpoint.

    This node is reached AFTER the agent swarm drafts a workflow.
    LangGraph will interrupt() here so the WebSocket layer can:
      1. Send a 'confirm' event to the frontend
      2. Wait for the user to approve or cancel
      3. Resume with confirmed=True or confirmed=False

    When resumed:
      - confirmed=True  → Committer fires, audit log written
      - confirmed=False → Workflow cancelled, audit log written
    """
    confirmed = state.get("confirmed")

    # ── Not yet confirmed: request HITL pause ──────────────────────────
    # (LangGraph interrupt raises NodeInterrupt; the WebSocket handler
    #  catches it, sends the confirmation event, then calls .update()
    #  with confirmed=True/False and resumes.)
    if confirmed is None:
        from langgraph.errors import NodeInterrupt
        raise NodeInterrupt("Awaiting user confirmation")

    workflow = state.get("drafted_workflow", {})
    intent   = state.get("intent", "UNKNOWN")
    now      = datetime.now(timezone.utc).isoformat()

    # ── User cancelled ─────────────────────────────────────────────────
    if not confirmed:
        state["execution_status"] = "cancelled"
        state["audit_log"] = {
            "timestamp":  now,
            "intent":     intent,
            "action":     workflow.get("action", "N/A"),
            "status":     "cancelled",
            "cancelled_by": "user",
        }
        state["stream_log"].append("❌ Transaction cancelled by user.")
        return state

    # ── User confirmed → Committer Agent ──────────────────────────────
    state["stream_log"].append("✅ Confirmed! Committing transaction...")

    # --- dispatch microservice calls based on intent ---
    if intent == "PAYMENT":
        result = _commit_payment(workflow)
    elif intent == "PLANNER":
        result = _commit_trip(workflow)
    else:
        # MERCHANT bypasses HITL entirely (Phase 3C), but handle gracefully
        result = {"status": "ok", "detail": "No commit needed for merchant insights"}

    state["execution_status"] = "committed" if result["status"] == "ok" else "failed"
    state["stream_log"].append(
        f"{'✅ Committed' if result['status'] == 'ok' else '❌ Commit failed'}: {result.get('detail', '')}"
    )

    # --- write audit log ---
    state["audit_log"] = {
        "timestamp":  now,
        "intent":     intent,
        "action":     workflow.get("action", "N/A"),
        "status":     state["execution_status"],
        "detail":     result.get("detail", ""),
        "workflow_snapshot": workflow,
    }

    state["stream_log"].append("📋 Audit log written.")
    return state


# ── Mock microservice dispatchers ─────────────────────────────────────────────
# Replace these stubs with real API calls (Paytm UPI, booking APIs, etc.)

def _commit_payment(workflow: dict) -> dict:
    payee  = workflow.get("payee", "Unknown")
    amount = workflow.get("amount", 0)
    upi_id = workflow.get("upi_id", "unknown@paytm")
    # TODO: call Paytm UPI microservice here
    return {
        "status": "ok",
        "detail": f"₹{amount} sent to {payee} ({upi_id}) via UPI",
    }


def _commit_trip(workflow: dict) -> dict:
    destination = workflow.get("destination", "Unknown")
    total_cost  = workflow.get("total_cost", 0)
    # TODO: call flight + hotel booking APIs here
    return {
        "status": "ok",
        "detail": f"Trip to {destination} booked for ₹{total_cost}",
    }
