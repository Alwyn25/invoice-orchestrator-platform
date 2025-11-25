import logging
from concurrent import futures
import grpc

# Import gRPC stubs and messages
from backend.mcp.grpc import mcp_pb2, mcp_pb2_grpc

# Import repository functions for DB access
from backend.mcp.db import repository

# Import the fake LLM client
from backend.mcp.llm.client import LLMClient

class MCPServicer(mcp_pb2_grpc.MCPServicer):
    """Implements the MCP gRPC service."""

    def __init__(self):
        self.llm_client = LLMClient()

    def SaveDocument(self, request, context):
        """Stores document metadata in the database."""
        logging.info(f"SaveDocument called for ingestion_id: {request.ingestion_id}")

        # The gRPC metadata is a map<string, string>, which is dict-like
        metadata_dict = dict(request.metadata)

        # You can handle file_bytes here, e.g., save to a file system or blob storage.
        # For now, we just acknowledge its presence.
        if request.file_bytes:
            logging.info(f"Received {len(request.file_bytes)} bytes for {request.ingestion_id}")

        doc = repository.save_document(
            ingestion_id=request.ingestion_id,
            file_name=request.file_name,
            file_url=request.file_url,
            metadata=metadata_dict
        )

        if doc:
            return mcp_pb2.SaveDocResp(
                ok=True,
                doc_ref=doc.ingestion_id,
                message="Document saved successfully."
            )
        else:
            context.set_details(f"Failed to save document {request.ingestion_id}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return mcp_pb2.SaveDocResp(ok=False, message="Database operation failed.")

    def GetDocument(self, request, context):
        """Retrieves document metadata from the database."""
        logging.info(f"GetDocument called for ingestion_id: {request.ingestion_id}")

        doc = repository.get_document(request.ingestion_id)

        if doc:
            # Convert metadata from JSONB (dict) to map<string, string>
            metadata_map = {k: str(v) for k, v in doc.metadata.items()} if doc.metadata else {}

            return mcp_pb2.GetDocResp(
                doc_ref=doc.ingestion_id,
                file_url=doc.file_url or "",
                file_bytes=b"",  # Not storing bytes in DB, return empty
                metadata=metadata_map
            )
        else:
            context.set_details(f"Document with ingestion_id '{request.ingestion_id}' not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return mcp_pb2.GetDocResp()

    def QueryLLM(self, request, context):
        """Queries the fake LLM."""
        logging.info(f"QueryLLM called with model: {request.model}")

        # Convert map<string, string> to dict
        options_dict = dict(request.options)

        result = self.llm_client.query(
            prompt=request.prompt,
            model=request.model,
            options=options_dict
        )

        return mcp_pb2.QueryLLMResp(
            text=result.get("text", ""),
            confidence=result.get("confidence", 0.0),
            raw_response=result.get("raw_response", "")
        )

    def WriteMetric(self, request, context):
        """Writes a metric to the database."""
        logging.info(f"WriteMetric called for agent: {request.agent}")

        success = repository.write_metric(
            agent=request.agent,
            ingestion_id=request.ingestion_id,
            metric_json=request.metric_json,
            metric_ts=request.metric_ts
        )

        if not success:
            context.set_details("Failed to write metric to database.")
            context.set_code(grpc.StatusCode.INTERNAL)

        return mcp_pb2.WriteAck(ok=success)

    def WriteAudit(self, request, context):
        """Writes an audit event to the database."""
        logging.info(f"WriteAudit called for agent: {request.agent}, action: {request.action}")

        success = repository.write_audit(
            agent=request.agent,
            action=request.action,
            reference_id=request.reference_id,
            payload_json=request.payload_json,
            ts=request.ts
        )

        if not success:
            context.set_details("Failed to write audit event to database.")
            context.set_code(grpc.StatusCode.INTERNAL)

        return mcp_pb2.WriteAck(ok=success)


def serve():
    """Starts the gRPC server and waits for termination."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mcp_pb2_grpc.add_MCPServicer_to_server(MCPServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("MCP gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
