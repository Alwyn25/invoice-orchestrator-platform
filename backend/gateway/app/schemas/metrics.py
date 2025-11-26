from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MetricIngestRequest(BaseModel):
    agent: str
    ingestion_id: Optional[str] = None
    metrics: dict
    metric_ts: Optional[datetime] = None
    tags: Optional[dict] = None

class DashboardMetricsResponse(BaseModel):
    total_events: int
    by_agent: dict
    time_range: dict
