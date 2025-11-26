from fastapi import APIRouter

from backend.gateway.app.schemas.reports import GenerateReportRequest, ReportStatusResponse
from backend.gateway.app.services.agents_client import AgentsClient
from backend.gateway.app.dependencies.grpc_clients import get_agents_client
from fastapi import Depends

router = APIRouter()

@router.post("/generate", response_model=ReportStatusResponse)
async def generate_report(request: GenerateReportRequest, agents_client: AgentsClient = Depends(get_agents_client)):
    response = agents_client.generate_report(
        validation_id=request.validation_id,
        schema_id=request.schema_id,
        user_id=request.user_id,
    )
    return ReportStatusResponse(report_id=response.report_id, status=response.status)

@router.get("/{report_id}", response_model=ReportStatusResponse)
async def get_report_status(report_id: str):
    # This is a stubbed response.
    # In a real implementation, you would query the MCP for the report status.
    return ReportStatusResponse(report_id=report_id, status="READY")
