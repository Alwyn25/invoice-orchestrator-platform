from backend.orchestrator.flow.graph import build_graph, OrchestrationState
from backend.shared.clients.mcp import MCPClient
from backend.shared.clients.agents import AgentsClient

class Clients:
    def __init__(self):
        self.mcp = MCPClient()
        self.agents = AgentsClient()

    def save_state(self, state: dict):
        ingestion_id = state.get("ingestion_id")
        if ingestion_id:
            self.mcp.save_orchestration(ingestion_id, state)

def run_flow(ingestion_id: str) -> dict:
    """
    Builds and executes the LangGraph orchestration flow.
    """
    clients = Clients()
    graph = build_graph(clients)

    initial_state = {"ingestion_id": ingestion_id}

    final_state_data = {}
    for state_update in graph.stream(initial_state):
        final_state_data.update(state_update)
        clients.save_state(final_state_data)

    return final_state_data

def resume_after_human_review(state: dict) -> dict:
    """
    Resumes the graph from the conversion node after human approval.
    """
    clients = Clients()
    graph = build_graph(clients)

    final_state_data = state.copy()
    for state_update in graph.stream(state, {"recursion_limit": 100, "start_node": "conversion"}):
        final_state_data.update(state_update)
        clients.save_state(final_state_data)

    return final_state_data
