import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.mcp.db.engine import SessionLocal
from backend.mcp.db.models import DocumentsIngested, Metrics, AgentAudit

logging.basicConfig(level=logging.INFO)

def save_document(ingestion_id: str, file_name: str, file_url: str, metadata: dict):
    """Saves a document record to the database."""
    try:
        with SessionLocal() as session:
            db_document = DocumentsIngested(
                ingestion_id=ingestion_id,
                file_name=file_name,
                file_url=file_url,
                metadata=metadata,
                source="grpc",  # Defaulting source
                status="received"  # Defaulting status
            )
            session.add(db_document)
            session.commit()
            session.refresh(db_document)
            logging.info(f"Successfully saved document {ingestion_id}")
            return db_document
    except Exception as e:
        logging.error(f"Error saving document metadata for {ingestion_id}: {e}")
        return None

def get_document(ingestion_id: str):
    """Retrieves a document by its ingestion ID."""
    try:
        with SessionLocal() as session:
            doc = session.query(DocumentsIngested).filter(DocumentsIngested.ingestion_id == ingestion_id).first()
            if doc:
                logging.info(f"Successfully retrieved document {ingestion_id}")
            else:
                logging.warning(f"Document {ingestion_id} not found")
            return doc
    except Exception as e:
        logging.error(f"Error getting document {ingestion_id}: {e}")
        return None

def write_metric(agent: str, ingestion_id: str, metric_json: str, metric_ts: int):
    """Writes a metric event to the database."""
    try:
        with SessionLocal() as session:
            metric_data = json.loads(metric_json)
            ts_datetime = datetime.fromtimestamp(metric_ts, tz=timezone.utc)

            db_metric = Metrics(
                agent=agent,
                ingestion_id=ingestion_id,
                metric_ts=ts_datetime,
                metrics=metric_data,
                tags={} # No tags in new proto, default to empty dict
            )
            session.add(db_metric)
            session.commit()
            logging.info(f"Successfully wrote metric for agent {agent}")
            return True
    except (json.JSONDecodeError, Exception) as e:
        logging.error(f"Error writing metric for agent {agent}: {e}")
        return False

def write_audit(agent: str, action: str, reference_id: str, payload_json: str, ts: int):
    """Writes an audit event to the database."""
    try:
        with SessionLocal() as session:
            payload_data = json.loads(payload_json)
            ts_datetime = datetime.fromtimestamp(ts, tz=timezone.utc)

            db_audit = AgentAudit(
                agent=agent,
                action=action,
                reference_id=reference_id,
                payload=payload_data,
                created_at=ts_datetime # Use timestamp from request
            )
            session.add(db_audit)
            session.commit()
            logging.info(f"Successfully wrote audit event for agent {agent}")
            return True
    except (json.JSONDecodeError, Exception) as e:
        logging.error(f"Error writing audit event for agent {agent}: {e}")
        return False
