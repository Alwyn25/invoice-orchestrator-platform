import logging
import grpc
from concurrent import futures
import uuid
import json
import time

from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.clients.mcp import MCPClient
from backend.agents.common.logging_config import configure_logging

class MappingServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def MapSchema(self, request, context):
        ocr_id = request.ocr_id
        logging.info(f"MapSchema called for ocr_id: {ocr_id}")
        start_time = time.time()

        try:
            ocr_output = self.mcp_client.get_ocr_output(ocr_id)
            if not ocr_output:
                raise Exception("OCR output not found.")

            detected_fields = ocr_output.get("detected_fields", {})

            mapped_schema = {
                "invoice_number": detected_fields.get("invoice_number"),
                "invoice_date": detected_fields.get("date"),
                "supplier_name": "Dummy Supplier",
                "total_amount": float(detected_fields.get("total", 0.0)),
                "tax_total": 0.0,
                "grand_total": float(detected_fields.get("total", 0.0)),
                "items": [{"description": "Dummy Item", "quantity": 1, "rate": 100.00, "tax_rate": 0, "tax_amount": 0, "total": 100.00, "hsn": "9988"}]
            }

            schema_id = f"MAP-{uuid.uuid4()}"

            # Save to mapped_schema via MCP
            self.mcp_client.write_audit(
                agent="mapping_agent",
                action="save_mapped_schema",
                reference_id=ocr_id,
                payload_json={
                    "schema_id": schema_id,
                    "mapped_schema": mapped_schema,
                }
            )

            mapping_time_ms = int((time.time() - start_time) * 1000)
            self.mcp_client.write_metric(
                agent="mapping_agent",
                ingestion_id=None, # In a real system, you would get this from the ocr_output
                metrics={"mapping_time_ms": mapping_time_ms, "fields_extracted": len(mapped_schema)},
            )

            return agent_comm_pb2.MapResponse(
                schema_id=schema_id,
                status="MAPPED",
                mapped_schema_json=json.dumps(mapped_schema)
            )

        except Exception as e:
            logging.error(f"Error during mapping for ocr_id {ocr_id}: {e}", exc_info=True)
            context.set_details(f"Mapping failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_comm_pb2.MapResponse(status="FAILED", message=str(e))

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
