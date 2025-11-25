from fastapi import APIRouter, UploadFile, Form, File, HTTPException
import json
import uuid
from typing import Optional

from backend.gateway.app.schemas.ingestion import IngestionUploadResponse
from backend.gateway.app.services.mcp_client import MCPClient
from backend.gateway.app.services.agents_client import AgentsClient
from backend.gateway.app.dependencies.grpc_clients import get_mcp_client, get_agents_client
from fastapi import Depends

router = APIRouter()

@router.post("/upload", response_model=IngestionUploadResponse)
async def upload_ingestion(
    payload: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    mcp_client: MCPClient = Depends(get_mcp_client),
    agents_client: AgentsClient = Depends(get_agents_client),
):
    if not file and not payload:
        raise HTTPException(status_code=400, detail="Either a file or a payload with a file_url must be provided.")

    ingestion_id = f"ING-{uuid.uuid4()}"
    metadata = json.loads(payload) if payload else {}
    file_url = metadata.get("file_url")

    if file:
        file_url = f"s3://dummy-bucket/{ingestion_id}/{file.filename}"
        # In a real implementation, you would upload the file to S3 here.

    if not file_url:
        raise HTTPException(status_code=400, detail="file_url must be provided in the payload if no file is uploaded.")

    mcp_client.save_document(
        ingestion_id=ingestion_id,
        file_name=file.filename if file else file_url.split("/")[-1],
        file_url=file_url,
        metadata=metadata
    )

    agents_client.start_ocr(
        ingestion_id=ingestion_id,
        file_url=file_url,
        metadata=metadata
    )

    return IngestionUploadResponse(
        ingestion_id=ingestion_id,
        status="ACCEPTED",
        message="Ingestion accepted, OCR started"
    )
