import grpc
import logging
import json
import time
from typing import Optional

from backend.mcp.grpc import mcp_pb2, mcp_pb2_grpc
from backend.shared.dependencies.config import get_settings

class MCPClient:
    def __init__(self):
        settings = get_settings()
        channel = grpc.insecure_channel(f"{settings.MCP_HOST}:{settings.MCP_PORT}")
        self.stub = mcp_pb2_grpc.MCPStub(channel)

    def save_document(self, ingestion_id: str, file_name: str, file_url: Optional[str], metadata: dict, file_bytes: Optional[bytes] = None) -> mcp_pb2.SaveDocResp:
        request = mcp_pb2.SaveDocReq(
            ingestion_id=ingestion_id,
            file_name=file_name,
            file_url=file_url,
            metadata=metadata,
            file_bytes=file_bytes,
        )
        return self.stub.SaveDocument(request)

    def write_metric(self, agent: str, ingestion_id: Optional[str], metrics: dict, metric_ts: Optional[int]):
        ts = metric_ts or int(time.time())
        request = mcp_pb2.WriteMetricReq(
            agent=agent,
            ingestion_id=ingestion_id,
            metric_json=json.dumps(metrics),
            metric_ts=ts,
        )
        self.stub.WriteMetric(request)

    def write_audit(self, agent: str, action: str, reference_id: str, payload: dict, ts: Optional[int]):
        timestamp = ts or int(time.time())
        request = mcp_pb2.WriteAuditReq(
            agent=agent,
            action=action,
            reference_id=reference_id,
            payload_json=json.dumps(payload),
            ts=timestamp,
        )
        self.stub.WriteAudit(request)

    def get_document(self, ingestion_id: str):
        request = mcp_pb2.GetDocReq(ingestion_id=ingestion_id)
        return self.stub.GetDocument(request)

    def save_orchestration(self, ingestion_id: str, state: dict):
        request = mcp_pb2.OrchestrationState(
            ingestion_id=ingestion_id,
            state_bytes=json.dumps(state).encode('utf-8'),
        )
        return self.stub.SaveOrchestration(request)

    def get_orchestration(self, ingestion_id: str):
        request = mcp_pb2.GetDocReq(ingestion_id=ingestion_id)
        response = self.stub.GetOrchestration(request)
        if response and response.ingestion_id:
            return json.loads(response.state_bytes.decode('utf-8'))
        return None

    def get_ocr_output(self, ocr_id: str):
        request = mcp_pb2.GetDocReq(ingestion_id=ocr_id)
        response = self.stub.GetOcrOutput(request)
        if response and response.ocr_id:
            return {
                "ocr_id": response.ocr_id,
                "ingestion_id": response.ingestion_id,
                "raw_text": response.raw_text,
                "detected_fields": json.loads(response.detected_fields.decode('utf-8')),
                "confidence": response.confidence,
                "status": response.status,
            }
        return None

    def get_mapped_schema(self, schema_id: str):
        request = mcp_pb2.GetDocReq(ingestion_id=schema_id)
        response = self.stub.GetMappedSchema(request)
        if response and response.schema_id:
            return {
                "schema_id": response.schema_id,
                "ocr_id": response.ocr_id,
                "mapped_data": json.loads(response.mapped_data.decode('utf-8')),
                "mapping_confidence": response.mapping_confidence,
            }
        return None

    def get_validation_logs(self, validation_id: str):
        request = mcp_pb2.GetDocReq(ingestion_id=validation_id)
        response = self.stub.GetValidationLogs(request)
        if response and response.validation_id:
            return {
                "validation_id": response.validation_id,
                "schema_id": response.schema_id,
                "status": response.status,
                "errors": json.loads(response.errors.decode('utf-8')),
                "warnings": json.loads(response.warnings.decode('utf-8')),
            }
        return None
