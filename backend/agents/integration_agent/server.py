import logging
import grpc
from concurrent import futures
import uuid

from backend.agents import agent_comm_pb2, agent_comm_pb2_grpc
from backend.agents.common.mcp_client import MCPClient
from backend.agents.common.logging_config import configure_logging

class IntegrationServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def PushIntegration(self, request, context):
        conversion_id = request.conversion_id
        logging.info(f"PushIntegration called for conversion_id: {conversion_id} with target {request.target}")

        integration_id = f"INTEGRATION-TEST-{uuid.uuid4()}"

        self.mcp_client.write_audit(
            agent="integration_agent",
            action="PushIntegration",
            reference_id=conversion_id,
            payload_json={"integration_id": integration_id, "target": request.target, "credentials_id": request.credentials_id}
        )

        return agent_comm_pb2.IntegrationResponse(
            integration_id=integration_id,
            status="POSTED"
        )

def serve():
    configure_logging("integration_agent")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_comm_pb2_grpc.add_AgentCommServicer_to_server(IntegrationServicer(), server)
    server.add_insecure_port("[::]:6006")
    server.start()
    logging.info("Integration agent gRPC server started on port 6006")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
