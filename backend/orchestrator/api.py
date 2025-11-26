from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.orchestrator import service
from backend.orchestrator.flow.graph import OrchestrationState
from backend.shared.clients.mcp import MCPClient

app = FastAPI(title="Orchestrator Service", version="1.0.0")

class HumanReviewRequest(BaseModel):
    decision: str
    notes: Optional[str] = None

@app.post("/orchestrate/{ingestion_id}")
def start_orchestration(ingestion_id: str):
    return service.run_flow(ingestion_id)

@app.post("/human-review/{ingestion_id}/resolve")
def resolve_human_review(ingestion_id: str, request: HumanReviewRequest):
    mcp_client = MCPClient()
    state_dict = mcp_client.get_orchestration(ingestion_id)

    if not state_dict:
        raise HTTPException(status_code=404, detail="Orchestration not found.")

    state = OrchestrationState(**state_dict)

    if state.status != "PENDING_REVIEW":
        raise HTTPException(status_code=400, detail="Orchestration is not pending human review.")

    if request.decision == "approve":
        state.requires_human_review = False
        state.valid = True
        state.status = "RESUMING"
        return service.resume_after_human_review(state.dict())
    elif request.decision == "reject":
        state.status = "REJECTED_BY_HUMAN"
        mcp_client.save_orchestration(ingestion_id, state.dict())
        return state.dict()
    else:
        raise HTTPException(status_code=400, detail="Invalid decision. Must be 'approve' or 'reject'.")

@app.get("/orchestrations/{ingestion_id}")
def get_orchestration_status(ingestion_id: str):
    mcp_client = MCPClient()
    state = mcp_client.get_orchestration(ingestion_id)
    if not state:
        raise HTTPException(status_code=404, detail="Orchestration not found.")
    return state

@app.get("/health")
def health_check():
    return {"status": "ok"}
