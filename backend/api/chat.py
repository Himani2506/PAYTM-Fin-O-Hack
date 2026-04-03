from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.state import AgentState
from app.pipeline import pipeline
import json, uuid

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # ── Resume path: frontend sends confirm/cancel ────────────────
            if message.get("type") == "confirm":
                thread_id = message.get("thread_id")
                confirmed  = message.get("confirmed", False)   # True or False
                config     = {"configurable": {"thread_id": thread_id}}

                await websocket.send_text(json.dumps({
                    "type": "thinking",
                    "message": "✅ Confirmed! Committing..." if confirmed else "❌ Cancelling transaction..."
                }))

                # Inject user's decision into the persisted state, then resume
                pipeline.update_state(
                    config,
                    {"confirmed": confirmed},
                    as_node="hitl"
                )
                result = pipeline.invoke(None, config)

                # Stream any new log lines
                for log in result.get("stream_log", []):
                    await websocket.send_text(json.dumps({
                        "type": "thinking",
                        "message": log
                    }))

                await websocket.send_text(json.dumps({
                    "type":       "committed",
                    "status":     result["execution_status"],
                    "audit_log":  result.get("audit_log"),
                    "stream_log": result.get("stream_log", [])
                }))
                continue

            # ── Fresh request path ─────────────────────────────────────────
            user_input = message.get("input", "")
            thread_id  = str(uuid.uuid4())          # unique thread per request
            config     = {"configurable": {"thread_id": thread_id}}

            await websocket.send_text(json.dumps({
                "type":    "thinking",
                "message": "Understanding your request..."
            }))

            state = AgentState(
                user_input=user_input,
                intent=None,
                drafted_workflow=None,
                execution_status="pending",
                messages=[],
                risk_score=None,
                memory_context=None,
                stream_log=[],
                confirmed=None,
                audit_log=None,
            )

            # Run pipeline — will PAUSE before hitl node for PAYMENT/PLANNER
            result = pipeline.invoke(state, config)

            for log in result.get("stream_log", []):
                await websocket.send_text(json.dumps({
                    "type":    "thinking",
                    "message": log
                }))

            # MERCHANT flows complete immediately (no HITL)
            if result["intent"] == "MERCHANT":
                await websocket.send_text(json.dumps({
                    "type":       "result",
                    "intent":     result["intent"],
                    "workflow":   result["drafted_workflow"],
                    "status":     result["execution_status"],
                    "stream_log": result["stream_log"]
                }))
            else:
                # PAYMENT / PLANNER — send confirmation request to frontend
                await websocket.send_text(json.dumps({
                    "type":       "confirm_required",       # frontend renders HITL screen
                    "thread_id":  thread_id,                # must be echoed back on confirm
                    "intent":     result["intent"],
                    "workflow":   result["drafted_workflow"],
                    "risk_score": result.get("risk_score"),
                    "stream_log": result["stream_log"]
                }))

    except WebSocketDisconnect:
        print("Client disconnected")
