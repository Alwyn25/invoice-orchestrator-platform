from pydantic import BaseModel
from typing import List

class Warning(BaseModel):
    warning_id: str
    ingestion_id: str
    validation_id: str
    field_name: str
    severity: str
    message: str
    acknowledged: bool

class WarningsListResponse(BaseModel):
    warnings: List[Warning]
