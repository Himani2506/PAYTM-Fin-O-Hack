from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.state import AgentState
from app.pipeline import pipeline
import json

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            user_input = message.get("input", "")

            await websocket.send_text(json.dumps({
                "type": "thinking",
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
                stream_log=[]
            )

            result = pipeline.invoke(state)

            for log in result["stream_log"]:
                await websocket.send_text(json.dumps({
                    "type": "thinking",
                    "message": log
                }))

            await websocket.send_text(json.dumps({
                "type": "result",
                "intent": result["intent"],
                "workflow": result["drafted_workflow"],
                "status": result["execution_status"],
                "stream_log": result["stream_log"]
            }))

    except WebSocketDisconnect:
        print("Client disconnected")