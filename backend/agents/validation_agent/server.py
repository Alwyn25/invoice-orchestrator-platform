import logging
import grpc
from concurrent import futures
import uuid
import json
import re
from datetime import datetime, timezone

from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.clients.mcp import MCPClient
from backend.agents.common.logging_config import configure_logging

def validate_gstin(gstin: str) -> bool:
    if not gstin:
        return False
    return re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}$", gstin) is not None

def validate_date(date_str: str) -> bool:
    if not date_str:
        return False
    try:
        invoice_date = datetime.fromisoformat(date_str).astimezone(timezone.utc)
        return invoice_date <= datetime.now(timezone.utc)
    except ValueError:
        return False

class ValidationServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def ValidateSchema(self, request, context):
        schema_id = request.schema_id
        logging.info(f"ValidateSchema called for schema_id: {schema_id}")

        try:
            mapped_schema = self.mcp_client.get_mapped_schema(schema_id)
            if not mapped_schema:
                raise Exception("Mapped schema not found.")

            errors = []
            warnings = []

            if not validate_gstin(mapped_schema.get("supplier_gstin")):
                errors.append("Invalid GSTIN format.")
            if not validate_date(mapped_schema.get("invoice_date")):
                errors.append("Invoice date is in the future or invalid.")

            for item in mapped_schema.get("items", []):
                if not item.get("hsn") or len(str(item.get("hsn"))) not in [4, 6, 8]:
                    warnings.append(f"Invalid HSN for item: {item.get('description')}")

            valid = not errors
            validation_id = f"VAL-{uuid.uuid4()}"

            # Save to validation_logs via MCP
            self.mcp_client.write_audit(
                agent="validation_agent",
                action="save_validation_log",
                reference_id=schema_id,
                payload_json={
                    "validation_id": validation_id, "valid": valid,
                    "errors": errors, "warnings": warnings
                }
            )

            return agent_comm_pb2.ValidateResponse(
                validation_id=validation_id,
                valid=valid,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            logging.error(f"Error during validation for schema_id {schema_id}: {e}", exc_info=True)
            context.set_details(f"Validation failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_comm_pb2.ValidateResponse()

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
