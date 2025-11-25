import os
import grpc
import logging
import json
import time
from typing import Optional

# Faking the import path for mcp_pb2 and mcp_pb2_grpc
# In a real monorepo setup, you would configure PYTHONPATH or use relative imports
# For this example, we assume they are importable.
from backend.mcp.grpc import mcp_pb2, mcp_pb2_grpc

class MCPClient:
    """A gRPC client for interacting with the MCP service."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        mcp_host = host or os.getenv("MCP_HOST", "localhost")
        mcp_port = port or int(os.getenv("MCP_PORT", "50051"))
        self._channel = grpc.insecure_channel(f"{mcp_host}:{mcp_port}")
        self._stub = mcp_pb2_grpc.MCPStub(self._channel)
        logging.info(f"MCPClient initialized for {mcp_host}:{mcp_port}")

    def write_metric(
        self,
        agent: str,
        ingestion_id: Optional[str],
        metric_json: dict,
        metric_ts: Optional[int] = None,
    ):
        """Writes a metric to the MCP."""
        try:
            ts = metric_ts or int(time.time())
            request = mcp_pb2.WriteMetricReq(
                agent=agent,
                ingestion_id=ingestion_id,
                metric_json=json.dumps(metric_json),
                metric_ts=ts,
            )
            response = self._stub.WriteMetric(request)
            if not response.ok:
                logging.error("MCP failed to write metric.")
        except grpc.RpcError as e:
            logging.error(f"gRPC error writing metric to MCP: {e.details()}")
        except Exception as e:
            logging.error(f"Error writing metric to MCP: {e}")

    def write_audit(
        self,
        agent: str,
        action: str,
        reference_id: str,
        payload_json: dict,
        ts: Optional[int] = None,
    ):
        """Writes an audit event to the MCP."""
        try:
            timestamp = ts or int(time.time())
            request = mcp_pb2.WriteAuditReq(
                agent=agent,
                action=action,
                reference_id=reference_id,
                payload_json=json.dumps(payload_json),
                ts=timestamp,
            )
            response = self._stub.WriteAudit(request)
            if not response.ok:
                logging.error("MCP failed to write audit event.")
        except grpc.RpcError as e:
            logging.error(f"gRPC error writing audit to MCP: {e.details()}")
        except Exception as e:
            logging.error(f"Error writing audit to MCP: {e}")

    def close(self):
        """Closes the gRPC channel."""
        if self._channel:
            self._channel.close()
