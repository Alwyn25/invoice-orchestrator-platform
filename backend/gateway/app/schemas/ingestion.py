from pydantic import BaseModel
from typing import Optional

class IngestionUploadResponse(BaseModel):
    ingestion_id: str
    status: str
    message: Optional[str] = None
