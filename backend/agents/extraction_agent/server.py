import logging
import grpc
from concurrent import futures
import uuid

from backend.agents import agent_comm_pb2, agent_comm_pb2_grpc
from backend.agents.common.mcp_client import MCPClient
from backend.agents.common.logging_config import configure_logging

class ExtractionServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def StartOCR(self, request, context):
        ingestion_id = request.ingestion.ingestion_id
        logging.info(f"StartOCR called for ingestion_id: {ingestion_id}")

        ocr_id = f"OCR-TEST-{uuid.uuid4()}"

        self.mcp_client.write_audit(
            agent="extraction_agent",
            action="StartOCR",
            reference_id=ingestion_id,
            payload_json={"ocr_id": ocr_id, "priority": request.priority}
        )

        return agent_comm_pb2.OCRResponse(
            ocr_id=ocr_id,
            status="EXTRACTED",
            message="Stub OCR completed"
        )

def serve():
    configure_logging("extraction_agent")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_comm_pb2_grpc.add_AgentCommServicer_to_server(ExtractionServicer(), server)
    server.add_insecure_port("[::]:6001")
    server.start()
    logging.info("Extraction agent gRPC server started on port 6001")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
