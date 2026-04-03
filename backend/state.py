from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    drafted_workflow: Optional[dict]
    execution_status: str
    messages: List[dict]
    risk_score: Optional[float]
    memory_context: Optional[str]
    stream_log: List[str]
    # Phase 4 — HITL
    confirmed: Optional[bool]       # True = user confirmed, False = cancelled
    audit_log: Optional[dict]       # written after commit