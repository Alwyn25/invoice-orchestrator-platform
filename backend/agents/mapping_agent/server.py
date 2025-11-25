import logging
import grpc
from concurrent import futures
import uuid
import json

from backend.agents import agent_comm_pb2, agent_comm_pb2_grpc
from backend.agents.common.mcp_client import MCPClient
from backend.agents.common.logging_config import configure_logging

class MappingServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def MapSchema(self, request, context):
        ocr_id = request.ocr_id
        logging.info(f"MapSchema called for ocr_id: {ocr_id}")

        schema_id = f"SCHEMA-TEST-{uuid.uuid4()}"

        self.mcp_client.write_audit(
            agent="mapping_agent",
            action="MapSchema",
            reference_id=ocr_id,
            payload_json={"schema_id": schema_id}
        )

        return agent_comm_pb2.MapResponse(
            schema_id=schema_id,
            status="MAPPED",
            mapped_schema_json=json.dumps({"field1": "value1", "field2": "value2"})
        )

def serve():
    configure_logging("mapping_agent")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_comm_pb2_grpc.add_AgentCommServicer_to_server(MappingServicer(), server)
    server.add_insecure_port("[::]:6002")
    server.start()
    logging.info("Mapping agent gRPC server started on port 6002")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
