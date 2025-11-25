import logging
import grpc
from concurrent import futures
import uuid

from backend.agents import agent_comm_pb2, agent_comm_pb2_grpc
from backend.agents.common.mcp_client import MCPClient
from backend.agents.common.logging_config import configure_logging

class ReportServicer(agent_comm_pb2_grpc.AgentCommServicer):
    def __init__(self):
        self.mcp_client = MCPClient()

    def GenerateReport(self, request, context):
        validation_id = request.validation_id
        logging.info(f"GenerateReport called for validation_id: {validation_id}")

        report_id = f"REPORT-TEST-{uuid.uuid4()}"

        self.mcp_client.write_audit(
            agent="report_agent",
            action="GenerateReport",
            reference_id=validation_id,
            payload_json={"report_id": report_id, "user_id": request.user_id}
        )

        return agent_comm_pb2.ReportResponse(
            report_id=report_id,
            status="READY"
        )

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
