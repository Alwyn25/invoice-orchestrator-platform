import grpc
from backend.shared.grpc import agent_comm_pb2, agent_comm_pb2_grpc
from backend.shared.dependencies.config import get_settings

class AgentsClient:
    def __init__(self):
        settings = get_settings()

        extraction_channel = grpc.insecure_channel(f"{settings.EXTRACTION_AGENT_HOST}:{settings.EXTRACTION_AGENT_PORT}")
        validation_channel = grpc.insecure_channel(f"{settings.VALIDATION_AGENT_HOST}:{settings.VALIDATION_AGENT_PORT}")
        report_channel = grpc.insecure_channel(f"{settings.REPORT_AGENT_HOST}:{settings.REPORT_AGENT_PORT}")
        conversion_channel = grpc.insecure_channel(f"{settings.CONVERSION_AGENT_HOST}:{settings.CONVERSION_AGENT_PORT}")
        integration_channel = grpc.insecure_channel(f"{settings.INTEGRATION_AGENT_HOST}:{settings.INTEGRATION_AGENT_PORT}")

        self.extraction_stub = agent_comm_pb2_grpc.AgentCommStub(extraction_channel)
        self.validation_stub = agent_comm_pb2_grpc.AgentCommStub(validation_channel)
        self.report_stub = agent_comm_pb2_grpc.AgentCommStub(report_channel)
        self.conversion_stub = agent_comm_pb2_grpc.AgentCommStub(conversion_channel)
        self.integration_stub = agent_comm_pb2_grpc.AgentCommStub(integration_channel)

    def start_ocr(self, ingestion_id: str, file_url: str, metadata: dict, priority: str = "normal") -> agent_comm_pb2.OCRResponse:
        ingestion_ref = agent_comm_pb2.IngestionRef(
            ingestion_id=ingestion_id,
            file_url=file_url,
            metadata=metadata,
        )
        request = agent_comm_pb2.OCRRequest(ingestion=ingestion_ref, priority=priority)
        return self.extraction_stub.StartOCR(request)

    def validate_schema(self, schema_id: str, ruleset: str = "default") -> agent_comm_pb2.ValidateResponse:
        request = agent_comm_pb2.ValidateRequest(schema_id=schema_id, ruleset=ruleset)
        return self.validation_stub.ValidateSchema(request)

    def generate_report(self, validation_id: str, schema_id: str, user_id: str) -> agent_comm_pb2.ReportResponse:
        request = agent_comm_pb2.ReportRequest(validation_id=validation_id, schema_id=schema_id, user_id=user_id)
        return self.report_stub.GenerateReport(request)

    def convert_to_tally(self, validation_id: str, dry_run: bool = False) -> agent_comm_pb2.ConvertResponse:
        request = agent_comm_pb2.ConvertRequest(validation_id=validation_id, target="tally", dry_run=dry_run)
        return self.conversion_stub.Convert(request)

    def convert_to_zoho(self, validation_id: str, dry_run: bool = False) -> agent_comm_pb2.ConvertResponse:
        request = agent_comm_pb2.ConvertRequest(validation_id=validation_id, target="zoho", dry_run=dry_run)
        return self.conversion_stub.Convert(request)

    def push_integration(self, conversion_id: str, target: str, credentials_id: str) -> agent_comm_pb2.IntegrationResponse:
        request = agent_comm_pb2.IntegrationRequest(conversion_id=conversion_id, target=target, credentials_id=credentials_id)
        return self.integration_stub.PushIntegration(request)
