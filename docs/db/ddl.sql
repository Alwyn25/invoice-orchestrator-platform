-- PostgreSQL 14+ Schema for AI-powered Invoice Validation & Platform Posting System

-- ENUM Types for status fields
CREATE TYPE source_enum AS ENUM ('upload', 'email', 's3', 'gdrive');
CREATE TYPE document_status_enum AS ENUM ('received', 'processing', 'completed', 'failed');
CREATE TYPE ocr_status_enum AS ENUM ('extracted', 'failed');
CREATE TYPE validation_status_enum AS ENUM ('VALID', 'INVALID');
CREATE TYPE target_enum AS ENUM ('tally', 'zoho');
CREATE TYPE conversion_status_enum AS ENUM ('converted', 'failed');
CREATE TYPE integration_status_enum AS ENUM ('posted', 'failed', 'pending');
CREATE TYPE report_status_enum AS ENUM ('generating', 'ready', 'failed');
CREATE TYPE severity_enum AS ENUM ('INFO', 'WARNING', 'ERROR');

-- Table: documents_ingested
CREATE TABLE documents_ingested (
    ingestion_id VARCHAR PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_url VARCHAR(1024),
    source source_enum NOT NULL,
    metadata JSONB,
    status document_status_enum NOT NULL DEFAULT 'received',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE documents_ingested IS 'Represents uploaded documents for processing.';
COMMENT ON COLUMN documents_ingested.ingestion_id IS 'Primary key, format: ING-YYYYMMDD-ID';
COMMENT ON COLUMN documents_ingested.file_name IS 'Original name of the uploaded file.';
COMMENT ON COLUMN documents_ingested.file_url IS 'Optional URL to the stored file (e.g., S3).';
COMMENT ON COLUMN documents_ingested.source IS 'Source of the document (upload, email, etc.).';
COMMENT ON COLUMN documents_ingested.metadata IS 'Additional metadata about the ingestion.';
COMMENT ON COLUMN documents_ingested.status IS 'Current processing status of the document.';
COMMENT ON COLUMN documents_ingested.created_at IS 'Timestamp of when the document was ingested.';
COMMENT ON COLUMN documents_ingested.updated_at IS 'Timestamp of the last update.';

-- Indexes for documents_ingested
CREATE INDEX idx_documents_ingested_created_at ON documents_ingested(created_at);
CREATE INDEX idx_documents_ingested_status ON documents_ingested(status);


-- Table: ocr_output
CREATE TABLE ocr_output (
    ocr_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_id VARCHAR NOT NULL,
    raw_text TEXT,
    detected_fields JSONB,
    confidence REAL,
    status ocr_status_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_ingestion
        FOREIGN KEY(ingestion_id)
        REFERENCES documents_ingested(ingestion_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE ocr_output IS 'Stores OCR text and detected fields from a document.';
COMMENT ON COLUMN ocr_output.ocr_id IS 'Primary key for the OCR output.';
COMMENT ON COLUMN ocr_output.ingestion_id IS 'Foreign key to the ingested document.';
COMMENT ON COLUMN ocr_output.raw_text IS 'The full raw text extracted by OCR.';
COMMENT ON COLUMN ocr_output.detected_fields IS 'JSONB of detected fields and their values.';
COMMENT ON COLUMN ocr_output.confidence IS 'Overall confidence score of the OCR extraction.';
COMMENT ON COLUMN ocr_output.status IS 'Status of the OCR extraction process.';

-- Index for ocr_output
CREATE INDEX idx_ocr_output_ingestion_id ON ocr_output(ingestion_id);


-- Table: mapped_schema
CREATE TABLE mapped_schema (
    schema_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ocr_id BIGINT NOT NULL,
    mapped_data JSONB NOT NULL,
    mapping_confidence REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_ocr
        FOREIGN KEY(ocr_id)
        REFERENCES ocr_output(ocr_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE mapped_schema IS 'Represents the canonical internal schema after mapping.';
COMMENT ON COLUMN mapped_schema.schema_id IS 'Primary key for the mapped schema.';
COMMENT ON COLUMN mapped_schema.ocr_id IS 'Foreign key to the OCR output.';
COMMENT ON COLUMN mapped_schema.mapped_data IS 'The structured data mapped to the internal schema.';
COMMENT ON COLUMN mapped_schema.mapping_confidence IS 'Confidence score of the schema mapping.';


-- Table: validation_logs
CREATE TABLE validation_logs (
    validation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    schema_id BIGINT NOT NULL,
    status validation_status_enum NOT NULL,
    errors JSONB,
    warnings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_schema
        FOREIGN KEY(schema_id)
        REFERENCES mapped_schema(schema_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE validation_logs IS 'Logs the results of schema validation.';
COMMENT ON COLUMN validation_logs.validation_id IS 'Primary key for the validation log.';
COMMENT ON COLUMN validation_logs.schema_id IS 'Foreign key to the mapped schema.';
COMMENT ON COLUMN validation_logs.status IS 'Overall validation status (VALID/INVALID).';
COMMENT ON COLUMN validation_logs.errors IS 'JSONB array of validation errors.';
COMMENT ON COLUMN validation_logs.warnings IS 'JSONB array of validation warnings.';


-- Table: conversion_logs
CREATE TABLE conversion_logs (
    conversion_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    validation_id BIGINT NOT NULL,
    target target_enum NOT NULL,
    output TEXT,
    artifact_url TEXT,
    status conversion_status_enum NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_validation
        FOREIGN KEY(validation_id)
        REFERENCES validation_logs(validation_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE conversion_logs IS 'Logs the conversion of validated data to external formats.';
COMMENT ON COLUMN conversion_logs.conversion_id IS 'Primary key for the conversion log.';
COMMENT ON COLUMN conversion_logs.validation_id IS 'Foreign key to the validation log.';
COMMENT ON COLUMN conversion_logs.target IS 'The target format for conversion (tally/zoho).';
COMMENT ON COLUMN conversion_logs.output IS 'The converted output as a string (XML/JSON).';
COMMENT ON COLUMN conversion_logs.artifact_url IS 'URL to the saved conversion artifact.';
COMMENT ON COLUMN conversion_logs.status IS 'Status of the conversion process.';


-- Table: integration_logs
CREATE TABLE integration_logs (
    integration_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversion_id BIGINT NOT NULL,
    target target_enum NOT NULL,
    platform_response TEXT,
    status integration_status_enum NOT NULL DEFAULT 'pending',
    retry INT DEFAULT 0,
    platform_status_code INT,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_conversion
        FOREIGN KEY(conversion_id)
        REFERENCES conversion_logs(conversion_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE integration_logs IS 'Logs attempts to post data to external platforms.';
COMMENT ON COLUMN integration_logs.integration_id IS 'Primary key for the integration log.';
COMMENT ON COLUMN integration_logs.conversion_id IS 'Foreign key to the conversion log.';
COMMENT ON COLUMN integration_logs.target IS 'The target platform for integration.';
COMMENT ON COLUMN integration_logs.platform_response IS 'Response from the external platform.';
COMMENT ON COLUMN integration_logs.status IS 'Status of the integration attempt.';
COMMENT ON COLUMN integration_logs.retry IS 'Number of retry attempts.';
COMMENT ON COLUMN integration_logs.platform_status_code IS 'HTTP status code from the platform.';
COMMENT ON COLUMN integration_logs.last_attempt_at IS 'Timestamp of the last integration attempt.';
COMMENT ON COLUMN integration_logs.next_retry_at IS 'Timestamp for the next scheduled retry.';


-- Table: reports
CREATE TABLE reports (
    report_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    validation_id BIGINT NOT NULL,
    schema_id BIGINT NOT NULL,
    user_id VARCHAR(255),
    status report_status_enum NOT NULL DEFAULT 'generating',
    summary JSONB,
    report_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_validation_report
        FOREIGN KEY(validation_id)
        REFERENCES validation_logs(validation_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_schema_report
        FOREIGN KEY(schema_id)
        REFERENCES mapped_schema(schema_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE reports IS 'Represents validation result summaries for users.';
COMMENT ON COLUMN reports.report_id IS 'Primary key for the report.';
COMMENT ON COLUMN reports.validation_id IS 'Foreign key to the validation log.';
COMMENT ON COLUMN reports.schema_id IS 'Foreign key to the mapped schema.';
COMMENT ON COLUMN reports.user_id IS 'Identifier for the user who initiated the process.';
COMMENT ON COLUMN reports.status IS 'Status of the report generation.';
COMMENT ON COLUMN reports.summary IS 'JSONB summary of the validation results.';
COMMENT ON COLUMN reports.report_url IS 'URL to the generated report file.';


-- Table: warnings_logs
CREATE TABLE warnings_logs (
    warning_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_id VARCHAR,
    validation_id BIGINT,
    field_name VARCHAR(255),
    severity severity_enum NOT NULL,
    message TEXT NOT NULL,
    suggested_fix JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_ingestion_warning
        FOREIGN KEY(ingestion_id)
        REFERENCES documents_ingested(ingestion_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_validation_warning
        FOREIGN KEY(validation_id)
        REFERENCES validation_logs(validation_id)
        ON DELETE SET NULL
);

COMMENT ON TABLE warnings_logs IS 'Stores detailed per-field errors or warnings.';
COMMENT ON COLUMN warnings_logs.warning_id IS 'Primary key for the warning.';
COMMENT ON COLUMN warnings_logs.ingestion_id IS 'FK to the ingested document (optional).';
COMMENT ON COLUMN warnings_logs.validation_id IS 'FK to the validation log (optional).';
COMMENT ON COLUMN warnings_logs.field_name IS 'The name of the field with the issue.';
COMMENT ON COLUMN warnings_logs.severity IS 'Severity of the warning (INFO, WARNING, ERROR).';
COMMENT ON COLUMN warnings_logs.message IS 'The warning or error message.';
COMMENT ON COLUMN warnings_logs.suggested_fix IS 'Suggested fix for the issue.';
COMMENT ON COLUMN warnings_logs.acknowledged IS 'Whether the warning has been acknowledged by a user.';


-- Table: metrics
CREATE TABLE metrics (
    metric_id SERIAL PRIMARY KEY,
    agent VARCHAR(255) NOT NULL,
    ingestion_id VARCHAR,
    metric_ts TIMESTAMP WITH TIME ZONE NOT NULL,
    metrics JSONB NOT NULL,
    tags JSONB
);

COMMENT ON TABLE metrics IS 'Stores OTel-like time-series metrics from agents.';
COMMENT ON COLUMN metrics.metric_id IS 'Primary key for the metric entry.';
COMMENT ON COLUMN metrics.agent IS 'The agent that emitted the metric.';
COMMENT ON COLUMN metrics.ingestion_id IS 'The ingestion ID related to this metric.';
COMMENT ON COLUMN metrics.metric_ts IS 'Timestamp of the metric measurement.';
COMMENT ON COLUMN metrics.metrics IS 'The actual metric data (e.g., counters, gauges).';
COMMENT ON COLUMN metrics.tags IS 'Tags for filtering and grouping metrics.';

-- Indexes for metrics
CREATE INDEX idx_metrics_metric_ts ON metrics(metric_ts);
CREATE INDEX idx_metrics_agent ON metrics(agent);
CREATE INDEX idx_metrics_ingestion_id ON metrics(ingestion_id);


-- Table: agent_audit
CREATE TABLE agent_audit (
    event_id BIGSERIAL PRIMARY KEY,
    agent VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    reference_id VARCHAR(255),
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE agent_audit IS 'Stores A2A and MCP events for traceability.';
COMMENT ON COLUMN agent_audit.event_id IS 'Primary key for the audit event.';
COMMENT ON COLUMN agent_audit.agent IS 'The agent performing the action.';
COMMENT ON COLUMN agent_audit.action IS 'The action being performed.';
COMMENT ON COLUMN agent_audit.reference_id IS 'Reference to a related entity (e.g., ingestion_id).';
COMMENT ON COLUMN agent_audit.payload IS 'The payload associated with the event.';
COMMENT ON COLUMN agent_audit.created_at IS 'Timestamp of the audit event.';

-- Indexes for agent_audit
CREATE INDEX idx_agent_audit_agent_created_at ON agent_audit(agent, created_at);
CREATE INDEX idx_agent_audit_reference_id ON agent_audit(reference_id);
