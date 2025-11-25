from fastapi import APIRouter

from backend.gateway.app.schemas.convert import ConversionRequest, ConversionResponse
from backend.gateway.app.services.agents_client import AgentsClient
from backend.gateway.app.dependencies.grpc_clients import get_agents_client
from fastapi import Depends

router = APIRouter()

@router.post("/tally", response_model=ConversionResponse)
async def convert_to_tally(request: ConversionRequest, agents_client: AgentsClient = Depends(get_agents_client)):
    response = agents_client.convert_to_tally(
        validation_id=request.validation_id,
        dry_run=request.dry_run
    )
    return ConversionResponse(
        conversion_id=response.conversion_id,
        status=response.status,
        artifact_url=response.artifact_url
    )

@router.post("/zoho", response_model=ConversionResponse)
async def convert_to_zoho(request: ConversionRequest, agents_client: AgentsClient = Depends(get_agents_client)):
    response = agents_client.convert_to_zoho(
        validation_id=request.validation_id,
        dry_run=request.dry_run
    )
    return ConversionResponse(
        conversion_id=response.conversion_id,
        status=response.status,
        artifact_url=response.artifact_url
    )
