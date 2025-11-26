from fastapi import APIRouter
from datetime import datetime

from backend.gateway.app.schemas.metrics import MetricIngestRequest, DashboardMetricsResponse
from backend.gateway.app.services.mcp_client import MCPClient
from backend.gateway.app.dependencies.grpc_clients import get_mcp_client
from fastapi import Depends

router = APIRouter()

@router.post("")
async def ingest_metric(request: MetricIngestRequest, mcp_client: MCPClient = Depends(get_mcp_client)):
    metric_ts = int(request.metric_ts.timestamp()) if request.metric_ts else None
    mcp_client.write_metric(
        agent=request.agent,
        ingestion_id=request.ingestion_id,
        metrics=request.metrics,
        metric_ts=metric_ts
    )
    return {"status": "OK"}

@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(from_ts: datetime, to_ts: datetime, agent: str = None):
    # This is a stubbed response.
    # In a real implementation, you would query the MCP for metrics.
    return DashboardMetricsResponse(
        total_events=123,
        by_agent={"extraction-agent": 50, "validation-agent": 73},
        time_range={"from": from_ts, "to": to_ts}
    )
