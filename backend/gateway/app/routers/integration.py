from fastapi import APIRouter

from backend.gateway.app.schemas.integration import IntegrationPushRequest, IntegrationStatusResponse
from backend.gateway.app.services.agents_client import AgentsClient
from backend.gateway.app.dependencies.grpc_clients import get_agents_client
from fastapi import Depends

router = APIRouter()

@router.post("/push", response_model=IntegrationStatusResponse)
async def push_integration(request: IntegrationPushRequest, agents_client: AgentsClient = Depends(get_agents_client)):
    response = agents_client.push_integration(
        conversion_id=request.conversion_id,
        target=request.target,
        credentials_id=request.credentials_id,
    )
    return IntegrationStatusResponse(integration_id=response.integration_id, status=response.status)
