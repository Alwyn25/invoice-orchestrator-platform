from functools import lru_cache
from fastapi import Depends

from backend.gateway.app.services.mcp_client import MCPClient
from backend.gateway.app.services.agents_client import AgentsClient
from backend.gateway.app.dependencies.config import Settings, get_settings

@lru_cache()
def get_mcp_client(settings: Settings = Depends(get_settings)) -> MCPClient:
    return MCPClient()

@lru_cache()
def get_agents_client(settings: Settings = Depends(get_settings)) -> AgentsClient:
    return AgentsClient()
