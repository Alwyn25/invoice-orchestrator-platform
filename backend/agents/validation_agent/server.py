import logging
import grpc
from concurrent import futures
import uuid

from backend.agents import agent_comm_pb2, agent_comm_pb2_grpc
from backend.agents.common.mcp_client import MCPClient
from backend.agents.common.logging_config import configure_logging

class ValidationServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def ValidateSchema(self, request, context):
        schema_id = request.schema_id
        logging.info(f"ValidateSchema called for schema_id: {schema_id}")

        validation_id = f"VALIDATION-TEST-{uuid.uuid4()}"

        self.mcp_client.write_audit(
            agent="validation_agent",
            action="ValidateSchema",
            reference_id=schema_id,
            payload_json={"validation_id": validation_id, "ruleset": request.ruleset}
        )

        return agent_comm_pb2.ValidateResponse(
            validation_id=validation_id,
            valid=True,
            errors=[],
            warnings=[]
        )

def serve():
    configure_logging("validation_agent")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_comm_pb2_grpc.add_AgentCommServicer_to_server(ValidationServicer(), server)
    server.add_insecure_port("[::]:6003")
    server.start()
    logging.info("Validation agent gRPC server started on port 6003")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
