import logging
from concurrent import futures
import grpc
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.timestamp_pb2 import Timestamp

# Import gRPC stubs
from backend.mcp.grpc import mcp_pb2
from backend.mcp.grpc import mcp_pb2_grpc

# Import database repository and models
from backend.mcp.db import repository
from backend.mcp.db.models import DocumentsIngested

# Import LLM client stub
from backend.mcp.llm.client import llm_client

# --- Helper Functions ---

def document_model_to_proto(doc_model: DocumentsIngested) -> mcp_pb2.Document:
    """Converts a SQLAlchemy DocumentsIngested model to a Protobuf Document message."""
    if not doc_model:
        return None

    doc_proto = mcp_pb2.Document(
        ingestion_id=doc_model.ingestion_id,
        file_name=doc_model.file_name,
        source=doc_model.source,
        status=doc_model.status,
    )

    if doc_model.file_url:
        doc_proto.file_url = doc_model.file_url

    if doc_model.metadata:
        ParseDict(doc_model.metadata, doc_proto.metadata)

    if doc_model.created_at:
        created_at_ts = Timestamp()
        created_at_ts.FromDatetime(doc_model.created_at)
        doc_proto.created_at.CopyFrom(created_at_ts)

    if doc_model.updated_at:
        updated_at_ts = Timestamp()
        updated_at_ts.FromDatetime(doc_model.updated_at)
        doc_proto.updated_at.CopyFrom(updated_at_ts)

    return doc_proto


# --- gRPC Servicer Implementation ---

class MCPServiceServicer(mcp_pb2_grpc.MCPServiceServicer):
    """Provides methods that implement functionality of MCP service."""

    def SaveDocument(self, request, context):
        logging.info(f"Received SaveDocument request for ingestion_id: {request.ingestion_id}")
        metadata_dict = MessageToDict(request.metadata)

        doc = repository.save_document_metadata(
            ingestion_id=request.ingestion_id,
            file_name=request.file_name,
            file_url=request.file_url,
            source=request.source,
            metadata=metadata_dict,
            status=request.status,
        )

        if doc:
            return mcp_pb2.SaveDocumentResponse(
                ingestion_id=doc.ingestion_id,
                message="Document metadata saved successfully."
            )
        else:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Failed to save document metadata.")
            return mcp_pb2.SaveDocumentResponse()

    def GetDocument(self, request, context):
        logging.info(f"Received GetDocument request for ingestion_id: {request.ingestion_id}")
        doc_model = repository.get_document_by_ingestion_id(request.ingestion_id)

        if doc_model:
            doc_proto = document_model_to_proto(doc_model)
            return mcp_pb2.GetDocumentResponse(document=doc_proto)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Document with ingestion_id '{request.ingestion_id}' not found.")
            return mcp_pb2.GetDocumentResponse()

    def WriteMetric(self, request, context):
        logging.info(f"Received WriteMetric request from agent: {request.agent}")
        metrics_dict = MessageToDict(request.metrics)
        tags_dict = MessageToDict(request.tags)
        metric_ts_dt = request.metric_ts.ToDatetime()

        repository.write_metric(
            agent=request.agent,
            ingestion_id=request.ingestion_id,
            metric_ts=metric_ts_dt,
            metrics_json=metrics_dict,
            tags_json=tags_dict,
        )

        return mcp_pb2.StatusResponse(success=True, message="Metric written successfully.")

    def WriteAudit(self, request, context):
        logging.info(f"Received WriteAudit request from agent: {request.agent} for action: {request.action}")
        payload_dict = MessageToDict(request.payload)

        repository.write_audit(
            agent=request.agent,
            action=request.action,
            reference_id=request.reference_id,
            payload_json=payload_dict,
        )

        return mcp_pb2.StatusResponse(success=True, message="Audit event written successfully.")

    def QueryLLM(self, request, context):
        logging.info("Received QueryLLM request.")
        context_dict = MessageToDict(request.context)

        response = llm_client.query(request.prompt, context_dict)

        response_proto = mcp_pb2.QueryLLMResponse(
            response_text=response.get("response_text", "")
        )
        if "metadata" in response and isinstance(response["metadata"], dict):
            ParseDict(response["metadata"], response_proto.metadata)

        return response_proto


# --- Server Setup ---

def serve():
    """Starts the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mcp_pb2_grpc.add_MCPServiceServicer_to_server(MCPServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("MCP gRPC server started on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
