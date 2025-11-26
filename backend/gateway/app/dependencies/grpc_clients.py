from functools import lru_cache
from fastapi import Depends

from backend.shared.clients.mcp import MCPClient
from backend.shared.clients.agents import AgentsClient
from backend.shared.dependencies.config import Settings, get_settings

@lru_cache()
def get_mcp_client(settings: Settings = Depends(get_settings)) -> MCPClient:
    return MCPClient()

@lru_cache()
def get_agents_client(settings: Settings = Depends(get_settings)) -> AgentsClient:
    return AgentsClient()
