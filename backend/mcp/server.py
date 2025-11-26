import logging
from concurrent import futures
import grpc
from fastapi import FastAPI
import uvicorn
import threading

# Import gRPC stubs and messages
from backend.shared.grpc import mcp_pb2, mcp_pb2_grpc
import json

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
            with open(f"/tmp/{request.ingestion_id}", "wb") as f:
                f.write(request.file_bytes)

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

            file_bytes = b""
            try:
                with open(f"/tmp/{doc.ingestion_id}", "rb") as f:
                    file_bytes = f.read()
            except FileNotFoundError:
                logging.warning(f"File not found for ingestion_id {doc.ingestion_id}")

            return mcp_pb2.GetDocResp(
                doc_ref=doc.ingestion_id,
                file_url=doc.file_url or "",
                file_bytes=file_bytes,
                metadata=metadata_map,
                file_name=doc.file_name,
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

    def SaveOrchestration(self, request, context):
        """Saves orchestration state to the database."""
        logging.info(f"SaveOrchestration called for ingestion_id: {request.ingestion_id}")
        state_dict = json.loads(request.state_bytes)
        success = repository.save_orchestration(
            ingestion_id=request.ingestion_id,
            state=state_dict
        )
        if not success:
            context.set_details("Failed to save orchestration state.")
            context.set_code(grpc.StatusCode.INTERNAL)
        return mcp_pb2.WriteAck(ok=success)

    def GetOrchestration(self, request, context):
        """Retrieves orchestration state from the database."""
        logging.info(f"GetOrchestration called for ingestion_id: {request.ingestion_id}")
        orchestration = repository.get_orchestration(request.ingestion_id)
        if orchestration:
            return mcp_pb2.OrchestrationState(
                ingestion_id=orchestration.ingestion_id,
                state_bytes=json.dumps(orchestration.state).encode('utf-8')
            )
        else:
            context.set_details(f"Orchestration with ingestion_id '{request.ingestion_id}' not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return mcp_pb2.OrchestrationState()

    def GetOcrOutput(self, request, context):
        ocr_output = repository.get_ocr_output(request.ingestion_id)
        if ocr_output:
            return mcp_pb2.OcrOutput(
                ocr_id=ocr_output.ocr_id,
                ingestion_id=ocr_output.ingestion_id,
                raw_text=ocr_output.raw_text,
                detected_fields=json.dumps(ocr_output.detected_fields).encode('utf-8'),
                confidence=ocr_output.confidence,
                status=ocr_output.status,
            )
        else:
            context.set_details(f"OCR output with id '{request.ingestion_id}' not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return mcp_pb2.OcrOutput()

    def GetMappedSchema(self, request, context):
        mapped_schema = repository.get_mapped_schema(request.ingestion_id)
        if mapped_schema:
            return mcp_pb2.MappedSchema(
                schema_id=mapped_schema.schema_id,
                ocr_id=mapped_schema.ocr_id,
                mapped_data=json.dumps(mapped_schema.mapped_data).encode('utf-8'),
                mapping_confidence=mapped_schema.mapping_confidence,
            )
        else:
            context.set_details(f"Mapped schema with id '{request.ingestion_id}' not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return mcp_pb2.MappedSchema()

    def GetValidationLogs(self, request, context):
        validation_logs = repository.get_validation_logs(request.ingestion_id)
        if validation_logs:
            return mcp_pb2.ValidationLogs(
                validation_id=validation_logs.validation_id,
                schema_id=validation_logs.schema_id,
                status=validation_logs.status,
                errors=json.dumps(validation_logs.errors).encode('utf-8'),
                warnings=json.dumps(validation_logs.warnings).encode('utf-8'),
            )
        else:
            context.set_details(f"Validation logs with id '{request.ingestion_id}' not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return mcp_pb2.ValidationLogs()


def serve():
    """Starts the gRPC server and waits for termination."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mcp_pb2_grpc.add_MCPServicer_to_server(MCPServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("MCP gRPC server started on port 50051")

    # Start FastAPI in a separate thread
    app = FastAPI()
    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    http_server = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"host": "0.0.0.0", "port": 8001})
    http_server.daemon = True
    http_server.start()

    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
