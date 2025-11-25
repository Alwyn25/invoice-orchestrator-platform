import grpc
import logging
import json
import time
from typing import Optional

from backend.mcp.grpc import mcp_pb2, mcp_pb2_grpc
from backend.gateway.app.dependencies.config import get_settings

class MCPClient:
    def __init__(self):
        settings = get_settings()
        channel = grpc.insecure_channel(f"{settings.MCP_HOST}:{settings.MCP_PORT}")
        self.stub = mcp_pb2_grpc.MCPStub(channel)

    def save_document(self, ingestion_id: str, file_name: str, file_url: Optional[str], metadata: dict) -> mcp_pb2.SaveDocResp:
        request = mcp_pb2.SaveDocReq(
            ingestion_id=ingestion_id,
            file_name=file_name,
            file_url=file_url,
            metadata=metadata,
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
