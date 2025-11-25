from fastapi import APIRouter
from typing import Optional

from backend.gateway.app.schemas.warnings import WarningsListResponse, Warning

router = APIRouter()

@router.get("", response_model=WarningsListResponse)
async def get_warnings(ingestion_id: Optional[str] = None, validation_id: Optional[str] = None):
    # This is a stubbed response.
    # In a real implementation, you would query the MCP for warnings.
    return WarningsListResponse(
        warnings=[
            Warning(
                warning_id="WARN-TEST-123",
                ingestion_id=ingestion_id or "ING-TEST-123",
                validation_id=validation_id or "VALID-TEST-123",
                field_name="invoice_date",
                severity="WARNING",
                message="Invoice date is in the future.",
                acknowledged=False
            )
        ]
    )
