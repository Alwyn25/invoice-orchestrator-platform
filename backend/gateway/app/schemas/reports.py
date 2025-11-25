from pydantic import BaseModel

class GenerateReportRequest(BaseModel):
    validation_id: str
    schema_id: str
    user_id: str

class ReportStatusResponse(BaseModel):
    report_id: str
    status: str
