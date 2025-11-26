import logging
import grpc
from concurrent import futures
import uuid
import os
import httpx
from datetime import datetime, timedelta

from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.clients.mcp import MCPClient
from backend.agents.common.logging_config import configure_logging

TALLY_URL = os.getenv("TALLY_URL", "http://localhost:9000")
ZOHO_BASE_URL = os.getenv("ZOHO_BASE_URL", "https://books.zoho.com/api/v3")

class IntegrationServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def PushIntegration(self, request, context):
        conversion_id = request.conversion_id
        logging.info(f"PushIntegration called for conversion_id: {conversion_id}, target: {request.target}")

        try:
            # In a real system, you would fetch the conversion output from the MCP
            output = "<ENVELOPE>...</ENVELOPE>" if request.target == "tally" else "{}"

            status = "PENDING"
            retry = 0
            next_retry_at = None

            try:
                if request.target == "tally":
                    response = httpx.post(TALLY_URL, content=output, headers={"Content-Type": "application/xml"})
                    response.raise_for_status()
                elif request.target == "zoho":
                    headers = {"Authorization": f"Zoho-oauthtoken {os.getenv('ZOHO_TOKEN')}"}
                    response = httpx.post(f"{ZOHO_BASE_URL}/invoices", content=output, headers=headers)
                    response.raise_for_status()

                status = "POSTED"

            except httpx.HTTPStatusError as e:
                status = "FAILED"
                retry = 1
                next_retry_at = datetime.utcnow() + timedelta(minutes=5)
                logging.error(f"HTTP error during integration for {conversion_id}: {e}")

            integration_id = f"INT-{request.target.upper()}-{uuid.uuid4()}"

            # Save to integration_logs via MCP
            self.mcp_client.write_audit(
                agent="integration_agent",
                action="save_integration_log",
                reference_id=conversion_id,
                payload_json={
                    "integration_id": integration_id, "target": request.target,
                    "status": status, "retry": retry
                }
            )

            return agent_comm_pb2.IntegrationResponse(
                integration_id=integration_id,
                status=status
            )

        except Exception as e:
            logging.error(f"Error during integration for conversion_id {conversion_id}: {e}", exc_info=True)
            context.set_details(f"Integration failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_comm_pb2.IntegrationResponse()

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
