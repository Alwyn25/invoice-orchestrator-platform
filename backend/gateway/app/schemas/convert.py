from pydantic import BaseModel
from typing import Optional

class ConversionRequest(BaseModel):
    validation_id: str
    dry_run: Optional[bool] = False
    template_version: Optional[str] = None

class ConversionResponse(BaseModel):
    conversion_id: str
    status: str
    artifact_url: str
