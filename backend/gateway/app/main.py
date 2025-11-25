from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.gateway.app.routers import ingestion, metrics, reports, convert, integration, warnings

app = FastAPI(
    title="Invoice Orchestrator Gateway",
    version="1.0.0",
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the routers
app.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(convert.router, prefix="/convert", tags=["convert"])
app.include_router(integration.router, prefix="/integration", tags=["integration"])
app.include_router(warnings.router, prefix="/warnings", tags=["warnings"])

@app.get("/health")
def health_check():
    """A simple health check endpoint."""
    return {"status": "ok"}
