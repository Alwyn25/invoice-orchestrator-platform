from sqlalchemy.orm import Session
from backend.mcp.db.engine import SessionLocal
from backend.mcp.db.models import DocumentsIngested, Metrics, AgentAudit
import logging

def save_document_metadata(ingestion_id: str, file_name: str, file_url: str, source: str, metadata: dict, status: str):
    """Saves document metadata to the database."""
    try:
        with SessionLocal() as session:
            db_document = DocumentsIngested(
                ingestion_id=ingestion_id,
                file_name=file_name,
                file_url=file_url,
                source=source,
                metadata=metadata,
                status=status
            )
            session.add(db_document)
            session.commit()
            session.refresh(db_document)
            return db_document
    except Exception as e:
        logging.error(f"Error saving document metadata: {e}")
        return None

def get_document_by_ingestion_id(ingestion_id: str):
    """Retrieves a document by its ingestion ID."""
    try:
        with SessionLocal() as session:
            return session.query(DocumentsIngested).filter(DocumentsIngested.ingestion_id == ingestion_id).first()
    except Exception as e:
        logging.error(f"Error getting document by ingestion ID: {e}")
        return None

def write_metric(agent: str, ingestion_id: str, metric_ts, metrics_json: dict, tags_json: dict):
    """Writes a metric event to the database."""
    try:
        with SessionLocal() as session:
            db_metric = Metrics(
                agent=agent,
                ingestion_id=ingestion_id,
                metric_ts=metric_ts,
                metrics=metrics_json,
                tags=tags_json
            )
            session.add(db_metric)
            session.commit()
    except Exception as e:
        logging.error(f"Error writing metric: {e}")
        return None

def write_audit(agent: str, action: str, reference_id: str, payload_json: dict):
    """Writes an audit event to the database."""
    try:
        with SessionLocal() as session:
            db_audit = AgentAudit(
                agent=agent,
                action=action,
                reference_id=reference_id,
                payload=payload_json
            )
            session.add(db_audit)
            session.commit()
    except Exception as e:
        logging.error(f"Error writing audit event: {e}")
        return None
