from pydantic import BaseModel
from typing import Optional

class IntegrationPushRequest(BaseModel):
    conversion_id: str
    target: str
    credentials_id: str
    callback_url: Optional[str] = None

class IntegrationStatusResponse(BaseModel):
    integration_id: str
    status: str
