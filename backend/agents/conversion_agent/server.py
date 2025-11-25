import logging
import grpc
from concurrent import futures
import uuid

from backend.agents import agent_comm_pb2, agent_comm_pb2_grpc
from backend.agents.common.mcp_client import MCPClient
from backend.agents.common.logging_config import configure_logging

class ConversionServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def Convert(self, request, context):
        validation_id = request.validation_id
        logging.info(f"Convert called for validation_id: {validation_id} with target {request.target}")

        conversion_id = f"CONVERSION-TEST-{uuid.uuid4()}"

        self.mcp_client.write_audit(
            agent="conversion_agent",
            action="Convert",
            reference_id=validation_id,
            payload_json={"conversion_id": conversion_id, "target": request.target, "dry_run": request.dry_run}
        )

        return agent_comm_pb2.ConvertResponse(
            conversion_id=conversion_id,
            status="CONVERTED",
            artifact_url=f"s3://dummy/artifact/{conversion_id}.xml"
        )

def serve():
    configure_logging("conversion_agent")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_comm_pb2_grpc.add_AgentCommServicer_to_server(ConversionServicer(), server)
    server.add_insecure_port("[::]:6005")
    server.start()
    logging.info("Conversion agent gRPC server started on port 6005")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
