import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.mcp.db.engine import Base

class DocumentsIngested(Base):
    __tablename__ = 'documents_ingested'
    ingestion_id = sa.Column(sa.String, primary_key=True)
    file_name = sa.Column(sa.String, nullable=False)
    file_url = sa.Column(sa.Text, nullable=True)
    source = sa.Column(sa.String)
    metadata = sa.Column(JSONB)
    status = sa.Column(sa.String)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
    updated_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())
    ocr_outputs = relationship("OcrOutput", back_populates="document_ingested")

class OcrOutput(Base):
    __tablename__ = 'ocr_output'
    ocr_id = sa.Column(sa.String, primary_key=True)
    ingestion_id = sa.Column(sa.String, sa.ForeignKey('documents_ingested.ingestion_id'))
    raw_text = sa.Column(sa.Text)
    detected_fields = sa.Column(JSONB)
    confidence = sa.Column(sa.Float)
    status = sa.Column(sa.String)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
    document_ingested = relationship("DocumentsIngested", back_populates="ocr_outputs")

class MappedSchema(Base):
    __tablename__ = 'mapped_schema'
    schema_id = sa.Column(sa.String, primary_key=True)
    ocr_id = sa.Column(sa.String, sa.ForeignKey('ocr_output.ocr_id'))
    mapped_data = sa.Column(JSONB)
    mapping_confidence = sa.Column(sa.Float)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())

class ValidationLogs(Base):
    __tablename__ = 'validation_logs'
    validation_id = sa.Column(sa.String, primary_key=True)
    schema_id = sa.Column(sa.String, sa.ForeignKey('mapped_schema.schema_id'))
    status = sa.Column(sa.String)
    errors = sa.Column(JSONB)
    warnings = sa.Column(JSONB)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())

class ConversionLogs(Base):
    __tablename__ = 'conversion_logs'
    conversion_id = sa.Column(sa.String, primary_key=True)
    validation_id = sa.Column(sa.String, sa.ForeignKey('validation_logs.validation_id'))
    target = sa.Column(sa.String)
    output = sa.Column(sa.Text)
    artifact_url = sa.Column(sa.Text)
    status = sa.Column(sa.String)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())

class IntegrationLogs(Base):
    __tablename__ = 'integration_logs'
    integration_id = sa.Column(sa.String, primary_key=True)
    conversion_id = sa.Column(sa.String, sa.ForeignKey('conversion_logs.conversion_id'))
    target = sa.Column(sa.String)
    platform_response = sa.Column(sa.Text)
    status = sa.Column(sa.String)
    retry = sa.Column(sa.Integer)
    platform_status_code = sa.Column(sa.Integer)
    last_attempt_at = sa.Column(sa.TIMESTAMP, nullable=True)
    next_retry_at = sa.Column(sa.TIMESTAMP, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())

class Reports(Base):
    __tablename__ = 'reports'
    report_id = sa.Column(sa.String, primary_key=True)
    validation_id = sa.Column(sa.String, sa.ForeignKey('validation_logs.validation_id'))
    schema_id = sa.Column(sa.String, sa.ForeignKey('mapped_schema.schema_id'))
    user_id = sa.Column(sa.String)
    status = sa.Column(sa.String)
    summary = sa.Column(JSONB)
    report_url = sa.Column(sa.Text)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
    updated_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now())

class WarningsLogs(Base):
    __tablename__ = 'warnings_logs'
    warning_id = sa.Column(sa.String, primary_key=True)
    ingestion_id = sa.Column(sa.String, nullable=True)
    validation_id = sa.Column(sa.String, nullable=True)
    field_name = sa.Column(sa.String)
    severity = sa.Column(sa.String)
    message = sa.Column(sa.Text)
    suggested_fix = sa.Column(JSONB)
    acknowledged = sa.Column(sa.Boolean)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())

class Metrics(Base):
    __tablename__ = 'metrics'
    metric_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    agent = sa.Column(sa.String)
    ingestion_id = sa.Column(sa.String, nullable=True)
    metric_ts = sa.Column(sa.TIMESTAMP)
    metrics = sa.Column(JSONB)
    tags = sa.Column(JSONB)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())

class AgentAudit(Base):
    __tablename__ = 'agent_audit'
    event_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    agent = sa.Column(sa.String)
    action = sa.Column(sa.String)
    reference_id = sa.Column(sa.String)
    payload = sa.Column(JSONB)
    created_at = sa.Column(sa.TIMESTAMP, server_default=sa.func.now())
