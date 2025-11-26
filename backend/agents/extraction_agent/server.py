import logging
import grpc
from concurrent import futures
import uuid
import time
import io

from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.clients.mcp import MCPClient
from backend.agents.common.logging_config import configure_logging
from backend.shared.services.ocr import get_ocr_service
from backend.shared.services.extractor import get_extractor_service

class ExtractionServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()
        self.ocr_service = get_ocr_service(self.mcp_client)
        self.extractor_service = get_extractor_service(self.mcp_client)

    def StartOCR(self, request, context):
        ingestion_id = request.ingestion.ingestion_id
        logging.info(f"StartOCR called for ingestion_id: {ingestion_id}")
        start_time = time.time()

        try:
            doc = self.mcp_client.get_document(ingestion_id)
            if not doc or not doc.file_bytes:
                raise Exception("Document not found or file_bytes is missing.")

            file_bytes = doc.file_bytes
            file_name = doc.file_name

            raw_text = self.ocr_service.perform_ocr(file_bytes, file_name)
            detected_fields = self.extractor_service.extract_schema(raw_text)

            ocr_id = f"OCR-{uuid.uuid4()}"

            self.mcp_client.write_audit(
                agent="extraction_agent",
                action="save_ocr_output",
                reference_id=ingestion_id,
                payload_json={
                    "ocr_id": ocr_id,
                    "status": "EXTRACTED",
                    "confidence": 0.85, # This would come from the extractor service
                    "detected_fields": detected_fields,
                }
            )

            ocr_time_ms = int((time.time() - start_time) * 1000)
            self.mcp_client.write_metric(
                agent="OCR-AG",
                ingestion_id=ingestion_id,
                metrics={"ocr_time_ms": ocr_time_ms, "text_length": len(raw_text), "success": True},
            )

            return agent_comm_pb2.OCRResponse(
                ocr_id=ocr_id,
                status="EXTRACTED",
                message="OCR and schema extraction completed successfully."
            )

        except Exception as e:
            logging.error(f"Error during extraction for ingestion_id {ingestion_id}: {e}", exc_info=True)
            ocr_time_ms = int((time.time() - start_time) * 1000)
            self.mcp_client.write_metric(
                agent="OCR-AG",
                ingestion_id=ingestion_id,
                metrics={"ocr_time_ms": ocr_time_ms, "success": False},
            )
            context.set_details(f"Extraction failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_comm_pb2.OCRResponse(status="FAILED", message=str(e))


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
