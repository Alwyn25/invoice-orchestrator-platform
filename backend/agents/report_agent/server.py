import logging
import grpc
from concurrent import futures
import uuid
import json

from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.clients.mcp import MCPClient
from backend.agents.common.logging_config import configure_logging

class ReportServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def GenerateReport(self, request, context):
        validation_id = request.validation_id
        logging.info(f"GenerateReport called for validation_id: {validation_id}")

        try:
            validation_logs = self.mcp_client.get_validation_logs(validation_id)
            if not validation_logs:
                raise Exception("Validation logs not found.")

            summary = {
                "status": "VALID" if not validation_logs["errors"] else "INVALID",
                "errors": validation_logs["errors"],
                "warnings": validation_logs["warnings"],
                "suggested_fixes": ["Check HSN code for item 'Dummy Item' against official sources."]
            }

            report_id = f"RPT-{uuid.uuid4()}"

            # Save to reports table via MCP
            self.mcp_client.write_audit(
                agent="report_agent",
                action="save_report",
                reference_id=validation_id,
                payload_json={
                    "report_id": report_id,
                    "status": "READY",
                    "summary": summary
                }
            )

            return agent_comm_pb2.ReportResponse(
                report_id=report_id,
                status="READY"
            )

        except Exception as e:
            logging.error(f"Error during report generation for validation_id {validation_id}: {e}", exc_info=True)
            context.set_details(f"Report generation failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return agent_comm_pb2.ReportResponse(status="FAILED", message=str(e))


def serve():
    configure_logging("report_agent")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agent_comm_pb2_grpc.add_AgentCommServicer_to_server(ReportServicer(), server)
    server.add_insecure_port("[::]:6004")
    server.start()
    logging.info("Report agent gRPC server started on port 6004")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
