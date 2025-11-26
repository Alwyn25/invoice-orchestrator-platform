import logging
import grpc
from concurrent import futures
import uuid
import json

from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.clients.mcp import MCPClient
from backend.agents.common.logging_config import configure_logging

def to_tally_xml(schema: dict) -> str:
    invoice_number = schema.get("invoice_number", "")
    return f"<ENVELOPE><VOUCHER><VOUCHERNUMBER>{invoice_number}</VOUCHERNUMBER></VOUCHER></ENVELOPE>"

def to_zoho_json(schema: dict) -> dict:
    return {
        "invoice_number": schema.get("invoice_number"),
        "date": schema.get("invoice_date"),
        "line_items": schema.get("items", []),
        "total": schema.get("grand_total")
    }

class ConversionServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def Convert(self, request, context):
        validation_id = request.validation_id
        logging.info(f"Convert called for validation_id: {validation_id}, target: {request.target}")

        try:
            # In a real system, you would fetch the mapped schema from the validation_id
            # This is not yet implemented in the MCP, so we'll stub it for now.
            mapped_schema = {
                "invoice_number": "INV-123", "invoice_date": "2025-11-25",
                "grand_total": 100.00, "items": []
            }

            output = ""
            if request.target == "tally":
                output = to_tally_xml(mapped_schema)
            elif request.target == "zoho":
                output = json.dumps(to_zoho_json(mapped_schema))
            else:
                raise ValueError("Invalid conversion target.")

            conversion_id = f"CONV-{request.target.upper()}-{uuid.uuid4()}"

            # Save to conversion_logs via MCP
            self.mcp_client.write_audit(
                agent="conversion_agent",
                action="save_conversion_log",
                reference_id=validation_id,
                payload_json={
                    "conversion_id": conversion_id, "target": request.target,
                    "output_snippet": output[:100],
                }
            )

            return agent_comm_pb2.ConvertResponse(
                conversion_id=conversion_id,
                status="CONVERTED",
                artifact_url=f"s3://dummy/{conversion_id}"
            )

        except Exception as e:
            logging.error(f"Error during conversion for validation_id {validation_id}: {e}", exc_info=True)
            context.set_details(f"Conversion failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_comm_pb2.ConvertResponse()

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
