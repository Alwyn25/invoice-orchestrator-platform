1) OpenAPI / Swagger (OpenAPI 3.0.3) — Full spec (YAML)

Save as `openapi.yml`. It's long — paste into Swagger Editor to explore.

```yaml
openapi: 3.0.3
info:
  title: Invoice Processing Platform API
  version: 1.0.0
  description: >
    REST Gateway for Ingestion->OCR->Mapping->Validation->Report->Conversion->Integration.
    Use JWT for user/service auth. Agents use service tokens or mTLS on gRPC.
servers:
  - url: https://api.example.com/v1
    description: Production
  - url: http://localhost:8000/v1
    description: Local

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-Service-Token

  schemas:
    IngestionRequest:
      type: object
      properties:
        source:
          type: string
          enum: [upload, email, s3, gdrive]
        file_name:
          type: string
        file_url:
          type: string
          description: "S3/GDrive URL alternative to raw file"
        metadata:
          type: object
          additionalProperties: true
      required: [source, file_name]
    IngestionResponse:
      type: object
      properties:
        ingestion_id:
          type: string
        status:
          type: string
        message:
          type: string

    OCRRequest:
      type: object
      properties:
        ingestion_id: { type: string }
        priority: { type: string, enum: [low, normal, high], default: normal }
      required: [ingestion_id]

    OCRResponse:
      type: object
      properties:
        ocr_id: { type: string }
        status: { type: string }

    MapRequest:
      type: object
      properties:
        ocr_id: { type: string }
      required: [ocr_id]

    MapResponse:
      type: object
      properties:
        schema_id: { type: string }
        status: { type: string }
        mapped_schema:
          type: object
          description: "Mapped invoice JSON"

    ValidateRequest:
      type: object
      properties:
        schema_id: { type: string }
        validate_ruleset: { type: string, default: "default" }
      required: [schema_id]

    ValidateResponse:
      type: object
      properties:
        validation_id: { type: string }
        status: { type: string, enum: [VALID, INVALID] }
        summary:
          type: object
          properties:
            errors: { type: integer }
            warnings: { type: integer }

    ReportGenerateRequest:
      type: object
      properties:
        validation_id: { type: string }
        schema_id: { type: string }
        user_id: { type: string }
        callback_url: { type: string }
      required: [validation_id, schema_id]

    ReportResponse:
      type: object
      properties:
        report_id: { type: string }
        status: { type: string, enum: [GENERATING, READY, FAILED] }

    ConversionRequest:
      type: object
      properties:
        validation_id: { type: string }
        dry_run: { type: boolean, default: false }
        template_version: { type: string }
      required: [validation_id]

    ConversionResponse:
      type: object
      properties:
        conversion_id: { type: string }
        status: { type: string }
        artifact_url: { type: string }

    IntegrationPushRequest:
      type: object
      properties:
        conversion_id: { type: string }
        target: { type: string, enum: [tally, zoho] }
        credentials_id: { type: string }
        callback_url: { type: string }
      required: [conversion_id, target, credentials_id]

    IntegrationResponse:
      type: object
      properties:
        integration_id: { type: string }
        status: { type: string }

    MetricPayload:
      type: object
      properties:
        agent: { type: string }
        ingestion_id: { type: string }
        metric_ts: { type: string, format: date-time }
        metrics: { type: object, additionalProperties: true }
        tags: { type: object, additionalProperties: true }

    Warning:
      type: object
      properties:
        warning_id: { type: string }
        ingestion_id: { type: string }
        validation_id: { type: string }
        field_name: { type: string }
        severity: { type: string, enum: [INFO, WARNING, ERROR] }
        message: { type: string }
        suggested_fix: { type: object }

paths:
  /ingestion/upload:
    post:
      summary: Upload a file or register a remote file for ingestion
      security:
        - BearerAuth: []
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                payload:
                  type: string
                  description: JSON string of IngestionRequest
      responses:
        "202":
          description: Accepted for processing
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/IngestionResponse"

  /ocr/extract:
    post:
      summary: Start OCR for an ingestion record
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/OCRRequest"
      responses:
        "200":
          description: OCR queued or started
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/OCRResponse"

  /schema/map:
    post:
      summary: Map OCR output to canonical schema
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/MapRequest"
      responses:
        "200":
          description: Mapping result
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/MapResponse"

  /schema/validate:
    post:
      summary: Validate a mapped schema (also triggers report generation)
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ValidateRequest"
      responses:
        "200":
          description: Validation result (synchronous)
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ValidateResponse"

  /reports/generate:
    post:
      summary: Generate end-user report (warnings/errors + PDF/JSON)
      security:
        - ApiKeyAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ReportGenerateRequest"
      responses:
        "202":
          description: Report generation accepted
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ReportResponse"

  /reports/{report_id}:
    get:
      summary: Fetch generated report
      security:
        - BearerAuth: []
      parameters:
        - name: report_id
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Report details
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ReportResponse"

  /convert/tally:
    post:
      summary: Convert validated schema to Tally XML
      security:
        - ApiKeyAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ConversionRequest"
      responses:
        "200":
          description: Conversion result
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ConversionResponse"

  /convert/zoho:
    post:
      summary: Convert validated schema to Zoho Books JSON
      security:
        - ApiKeyAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/ConversionRequest"
      responses:
        "200":
          description: Conversion result
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ConversionResponse"

  /integration/push:
    post:
      summary: Push converted artifact to external platform (Tally/Zoho)
      security:
        - ApiKeyAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/IntegrationPushRequest"
      responses:
        "202":
          description: Integration enqueued
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/IntegrationResponse"

  /metrics:
    post:
      summary: Push agent metrics (for dashboard)
      security:
        - ApiKeyAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/MetricPayload"
      responses:
        "200":
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
    get:
      summary: Query aggregated metrics for dashboard
      security:
        - BearerAuth: []
      parameters:
        - name: from
          in: query
          schema: { type: string, format: date-time }
        - name: to
          in: query
          schema: { type: string, format: date-time }
        - name: agent
          in: query
          schema: { type: string }
      responses:
        "200":
          description: Aggregated metrics
          content:
            application/json:
              schema:
                type: object
                additionalProperties: true

  /warnings:
    get:
      summary: Get warnings/errors for ingestion or validation
      security:
        - BearerAuth: []
      parameters:
        - name: ingestion_id
          in: query
          schema: { type: string }
        - name: validation_id
          in: query
          schema: { type: string }
      responses:
        "200":
          description: list of warnings
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Warning"

  /warnings/ack:
    post:
      summary: Acknowledge warnings
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                warning_ids:
                  type: array
                  items: { type: string }
      responses:
        "200":
          description: updated

security:
  - BearerAuth: []
```

---

# 2) gRPC Contract Files (`.proto`)

Save the following two files as `agent_comm.proto` and `mcp.proto`.

### agent_comm.proto (A2A agent-to-agent)

```proto
syntax = "proto3";
package agent;

option go_package = "github.com/yourorg/agentpb;agentpb";

// Common messages
message IngestionRef {
  string ingestion_id = 1;
  string file_url = 2;
  map<string,string> metadata = 3;
}

message OCRRequest {
  IngestionRef ingestion = 1;
  string priority = 2;
}
message OCRResponse {
  string ocr_id = 1;
  string status = 2;
  string message = 3;
}

message MapRequest {
  string ocr_id = 1;
}
message MapResponse {
  string schema_id = 1;
  string status = 2;
  string mapped_schema_json = 3;
}

message ValidateRequest {
  string schema_id = 1;
  string ruleset = 2;
}
message ValidateResponse {
  string validation_id = 1;
  bool valid = 2;
  repeated string errors = 3;
  repeated string warnings = 4;
  string summary_json = 5;
}

message ConvertRequest {
  string validation_id = 1;
  string target = 2; // tally | zoho
  bool dry_run = 3;
  string template_version = 4;
}
message ConvertResponse {
  string conversion_id = 1;
  string location = 2; // s3 url or inline artifact
  string status = 3;
}

message AgentEvent {
  string agent = 1;
  string event_type = 2;
  string reference_id = 3;
  string payload_json = 4;
  int64 ts = 5;
}
message AgentAck {
  string status = 1;
  string message = 2;
}

// Service definition
service AgentComm {
  rpc StartOCR(OCRRequest) returns (OCRResponse);
  rpc MapSchema(MapRequest) returns (MapResponse);
  rpc ValidateSchema(ValidateRequest) returns (ValidateResponse);
  rpc Convert(ConvertRequest) returns (ConvertResponse);

  // Bi-directional stream for events and acks
  rpc EventStream(stream AgentEvent) returns (stream AgentAck);
}
```

### mcp.proto (MCP: DB + LLM access, audit, metrics)

```proto
syntax = "proto3";
package mcp;

option go_package = "github.com/yourorg/mcppb;mcppb";

message SaveDocReq {
  string ingestion_id = 1;
  bytes file_bytes = 2;
  string file_url = 3;
  map<string,string> metadata = 4;
}
message SaveDocResp {
  bool ok = 1;
  string doc_ref = 2;
  string message = 3;
}

message GetDocReq {
  string ingestion_id = 1;
}
message GetDocResp {
  string doc_ref = 1;
  string file_url = 2;
  bytes file_bytes = 3;
  map<string,string> metadata = 4;
}

message QueryLLMReq {
  string prompt = 1;
  string model = 2;
  map<string,string> options = 3;
}
message QueryLLMResp {
  string text = 1;
  float confidence = 2;
  string raw_response = 3;
}

message WriteMetric {
  string agent = 1;
  string ingestion_id = 2;
  string metric_json = 3;
  int64 metric_ts = 4;
}
message WriteAck {
  bool ok = 1;
}

message WriteAudit {
  string agent = 1;
  string action = 2;
  string reference_id = 3;
  string payload_json = 4;
  int64 ts = 5;
}

service MCP {
  rpc SaveDocument(SaveDocReq) returns (SaveDocResp);
  rpc GetDocument(GetDocReq) returns (GetDocResp);
  rpc QueryLLM(QueryLLMReq) returns (QueryLLMResp);
  rpc WriteMetric(WriteMetric) returns (WriteAck);
  rpc WriteAudit(WriteAudit) returns (WriteAck);
}
```

**Notes for gRPC usage**

* Include JWT in metadata (`authorization: Bearer <token>`) and use mTLS for services-to-services.
* Use streaming for OCR progress and long conversions (EventStream).
* Add health checking proto or use gRPC health protocol.

---

# 3) Dashboard UI Mockups (wireframes + component descriptions)

Below are wireframes (ASCII art) + component lists + exact API endpoints used.

## 3.1 App-level nav

Top nav: Logo | Dashboard | Ingestions | Reports | Integrations | Settings | (User)

---

## 3.2 Dashboard — Wireframe (Main view)

```
+-------------------------------------------------------------------------------+
| Dashboard                                [Date range picker] [Refresh] [Export]|
+-------------------------------------------------------------------------------+
| KPIs:  [Total Processed: 3,512] [Pass Rate: 92.3%] [Avg OCR (s): 5.4] [Pending: 12] |
+-------------------------------------------------------------------------------+
| Left column (70%)                          | Right column (30%)               |
| - Recent ingestions list (table)           | - Metrics timeseries (line)      |
|   columns: ingestion_id, vendor, date,     |   Chart: validation pass rate    |
|   status (processing/valid/invalid), action| - Top errors (bar)               |
|   (view/report)                            | - Agent Health (cards)           |
| - Search & filters                         | - Alerts/Warn count              |
| - Latest 24h errors (list)                 | - Integration status (tally/zoho)|
+-------------------------------------------------------------------------------+
| Bottom: Recent Reports (table) [Download]                                          |
+-------------------------------------------------------------------------------+
```

### Components & Data sources

* KPI chips: `/v1/metrics?from=...&to=...` + aggregated DB queries.
* Recent ingestions table: GET `/v1/ingestions?limit=50` (not in spec; implement for UI).
* Timeseries charts (line): GET `/v1/metrics/dashboard?agent=VAL-AG&from=...`.
* Top errors: GET `/v1/warnings?from=...&to=...&severity=ERROR`.
* Integration status: read from `integration_logs` via API `/v1/integrations/status`.

### Interactions

* Click an ingestion → open Ingestion detail modal: shows OCR raw text, mapped schema, validation summary, `View Report` (GET `/v1/reports/{report_id}`), `Retry Conversion`, `Push to Platform`.

---

## 3.3 Ingestion Detail page (wireframe)

```
[ING-20251125-0001]  Vendor: TCS  Date: 2025-11-25   Status: INVALID

Tabs: [Overview] [OCR Text] [Mapped Schema] [Validation] [Reports] [Conversion]

Overview:
  - Download original file (link)
  - timeline: Uploaded -> OCR done -> Mapped -> Validated -> Report generated

OCR Text:
  - Show OCR raw_text (with page toggle)

Mapped Schema:
  - JSON viewer with mapped fields & mapping_confidence

Validation:
  - Errors list (red)
  - Warnings list (yellow)
  - Buttons: Acknowledge Warnings, Request Manual Review

Reports:
  - Link to PDF / JSON (GET /v1/reports/{report_id})

Conversion:
  - Tally XML (preview)
  - Zoho JSON (preview)
  - Buttons: Convert (POST /v1/convert/tally), Convert (POST /v1/convert/zoho)
```

---

# 4) Sample DB DDL + Test Data (Postgres)

Run in Postgres. We'll include DDL for core tables and a small data dump with 2 sample invoices (one valid, one invalid). Save as `db_schema.sql`.

```sql
-- Schema DDL
CREATE TABLE documents_ingested (
  ingestion_id VARCHAR PRIMARY KEY,
  file_name VARCHAR,
  file_url TEXT,
  source VARCHAR,
  metadata JSONB,
  status VARCHAR,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE ocr_output (
  ocr_id VARCHAR PRIMARY KEY,
  ingestion_id VARCHAR REFERENCES documents_ingested(ingestion_id),
  raw_text TEXT,
  detected_fields JSONB,
  confidence FLOAT,
  status VARCHAR,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE mapped_schema (
  schema_id VARCHAR PRIMARY KEY,
  ocr_id VARCHAR REFERENCES ocr_output(ocr_id),
  mapped_data JSONB,
  mapping_confidence FLOAT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE validation_logs (
  validation_id VARCHAR PRIMARY KEY,
  schema_id VARCHAR REFERENCES mapped_schema(schema_id),
  status VARCHAR,
  errors JSONB,
  warnings JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE conversion_logs (
  conversion_id VARCHAR PRIMARY KEY,
  validation_id VARCHAR REFERENCES validation_logs(validation_id),
  target VARCHAR,
  output TEXT,
  artifact_url TEXT,
  status VARCHAR,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE integration_logs (
  integration_id VARCHAR PRIMARY KEY,
  conversion_id VARCHAR REFERENCES conversion_logs(conversion_id),
  target VARCHAR,
  platform_response TEXT,
  status VARCHAR,
  retry INT DEFAULT 0,
  platform_status_code INT,
  last_attempt_at TIMESTAMP,
  next_retry_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE reports (
  report_id VARCHAR PRIMARY KEY,
  validation_id VARCHAR REFERENCES validation_logs(validation_id),
  schema_id VARCHAR REFERENCES mapped_schema(schema_id),
  user_id VARCHAR,
  status VARCHAR,
  summary JSONB,
  report_url TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP
);

CREATE TABLE warnings_logs (
  warning_id VARCHAR PRIMARY KEY,
  ingestion_id VARCHAR,
  validation_id VARCHAR,
  field_name VARCHAR,
  severity VARCHAR,
  message TEXT,
  suggested_fix JSONB,
  acknowledged BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE metrics (
  metric_id BIGSERIAL PRIMARY KEY,
  agent VARCHAR,
  ingestion_id VARCHAR,
  metric_ts TIMESTAMP,
  metrics JSONB,
  tags JSONB,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE agent_audit (
  event_id BIGSERIAL PRIMARY KEY,
  agent VARCHAR,
  action VARCHAR,
  reference_id VARCHAR,
  payload JSONB,
  created_at TIMESTAMP DEFAULT now()
);

-- Sample data: two ingestions (one valid, one invalid)
INSERT INTO documents_ingested (ingestion_id, file_name, file_url, source, metadata, status)
VALUES
('ING-20251125-0001','inv_tcs_1001.pdf','s3://invoices/inv_tcs_1001.pdf','upload','{"vendor":"TCS","received_date":"2025-11-25"}','PROCESSING'),
('ING-20251125-0002','inv_xyz_2001.pdf','s3://invoices/inv_xyz_2001.pdf','upload','{"vendor":"XYZ Pvt Ltd","received_date":"2025-11-25"}','PROCESSING');

-- OCR outputs
INSERT INTO ocr_output (ocr_id, ingestion_id, raw_text, detected_fields, confidence, status)
VALUES
('OCR-0001','ING-20251125-0001','Invoice No: INV-1001\nDate: 2025-11-01\nTotal: 11800','{"invoice_number":"INV-1001","date":"2025-11-01","total":11800,"vendor":"TCS"}',0.95,'EXTRACTED'),
('OCR-0002','ING-20251125-0002','Invoice No: INV-2001\nDate: 2026-01-01\nTotal: 1000','{"invoice_number":"INV-2001","date":"2026-01-01","total":1000,"vendor":"XYZ Pvt Ltd"}',0.92,'EXTRACTED');

-- Mapping
INSERT INTO mapped_schema (schema_id, ocr_id, mapped_data, mapping_confidence)
VALUES
('MAP-0001','OCR-0001','{
  "invoice_number":"INV-1001",
  "invoice_date":"2025-11-01",
  "supplier_name":"TCS",
  "supplier_gstin":"27AAAAA0000A1Z5",
  "buyer_name":"Corp Ltd",
  "items":[{"description":"Service","hsn":"9983","qty":1,"rate":10000,"tax_rate":18,"tax_amount":1800,"total":11800}],
  "total_amount":11800,
  "tax_total":1800,
  "grand_total":11800
}',0.93),
('MAP-0002','OCR-0002','{
  "invoice_number":"INV-2001",
  "invoice_date":"2026-01-01",
  "supplier_name":"XYZ Pvt Ltd",
  "supplier_gstin":"INVALID_GST",
  "buyer_name":"Corp Ltd",
  "items":[{"description":"Goods","hsn":"1234","qty":1,"rate":1000,"tax_rate":18,"tax_amount":180,"total":1180}],
  "total_amount":1000,
  "tax_total":180,
  "grand_total":1180
}',0.9);

-- Validation logs (first valid, second invalid: future date and invalid GST)
INSERT INTO validation_logs (validation_id, schema_id, status, errors, warnings)
VALUES
('VAL-0001','MAP-0001','VALID','[]','[]'),
('VAL-0002','MAP-0002','INVALID','["invoice_date:future_date","supplier_gstin:invalid_format"]','["amount_mismatch:items_sum_ne_total"]');

-- Reports
INSERT INTO reports (report_id, validation_id, schema_id, user_id, status, summary, report_url)
VALUES
('RPT-0001','VAL-0001','MAP-0001','user-admin','READY','{"errors":[],"warnings":[]}','s3://reports/RPT-0001.pdf'),
('RPT-0002','VAL-0002','MAP-0002','user-admin','READY','{"errors":["invoice_date:future_date","supplier_gstin:invalid_format"],"warnings":["amount_mismatch:items_sum_ne_total"]}','s3://reports/RPT-0002.pdf');

-- Conversion artifacts (only the first converted)
INSERT INTO conversion_logs (conversion_id, validation_id, target, output, artifact_url, status)
VALUES
('TXML-0001','VAL-0001','tally','<VOUCHER>...','s3://artifacts/TXML-0001.xml','CONVERTED'),
('ZJSON-0001','VAL-0001','zoho','{"invoice_number":"INV-1001"}','s3://artifacts/ZJSON-0001.json','CONVERTED');

-- Integration logs
INSERT INTO integration_logs (integration_id, conversion_id, target, platform_response, status, retry)
VALUES
('INT-0001','TXML-0001','tally','{"status":"created"}','POSTED',0),
('INT-0002','ZJSON-0001','zoho','{"code":0,"message":"success"}','POSTED',0);

-- sample warnings logs
INSERT INTO warnings_logs (warning_id, ingestion_id, validation_id, field_name, severity, message, suggested_fix)
VALUES
('WARN-0001','ING-20251125-0002','VAL-0002','invoice_date','ERROR','Invoice date 2026-01-01 is in the future', '{"fix":"ask user to confirm date"}'),
('WARN-0002','ING-20251125-0002','VAL-0002','supplier_gstin','ERROR','GSTIN format invalid', '{"fix":"verify GSTIN or set supplier as unregistered"}');

-- metrics
INSERT INTO metrics (agent, ingestion_id, metric_ts, metrics, tags)
VALUES
('OCR-AG','ING-20251125-0001',now(),'{"ocr_time_ms":4200,"pages":2,"confidence_avg":0.95}','{"queue":"normal"}'),
('VAL-AG','ING-20251125-0001',now(),'{"validation_time_ms":1200,"rules_run":32,"errors":0}','{}');
```

---

# 5) Test Invoice JSONs (2 invoices: valid & invalid)

Save as `test_invoices.json` — useful for unit tests / integration tests.

```json
[
  {
    "ingestion_id": "ING-20251125-0001",
    "file_name": "inv_tcs_1001.pdf",
    "mapped_schema": {
      "invoice_number":"INV-1001",
      "invoice_date":"2025-11-01",
      "supplier_name":"TCS",
      "supplier_gstin":"27AAAAA0000A1Z5",
      "buyer_name":"Corp Ltd",
      "items":[{"description":"Service","hsn":"9983","qty":1,"rate":10000,"tax_rate":18,"tax_amount":1800,"total":11800}],
      "total_amount":11800,
      "tax_total":1800,
      "grand_total":11800
    }
  },
  {
    "ingestion_id": "ING-20251125-0002",
    "file_name": "inv_xyz_2001.pdf",
    "mapped_schema": {
      "invoice_number":"INV-2001",
      "invoice_date":"2026-01-01",
      "supplier_name":"XYZ Pvt Ltd",
      "supplier_gstin":"INVALID_GST",
      "buyer_name":"Corp Ltd",
      "items":[{"description":"Goods","hsn":"1234","qty":1,"rate":1000,"tax_rate":18,"tax_amount":180,"total":1180}],
      "total_amount":1000,
      "tax_total":180,
      "grand_total":1180
    }
  }
]
```

---

# 6) Validation Rules — canonical summary (for engine implementation)

Implement these as ordered rules; return detailed error object with `field`, `rule`, `message`, `severity`, `fix_suggestion`.

1. **GSTIN Format**

   * Rule: `regex: ^\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z0-9]Z[A-Z0-9]$`
   * Severity: ERROR
   * Fix: "Verify GSTIN or mark supplier as unregistered."

2. **Invoice Date Not Future**

   * Rule: `invoice_date <= now()`
   * Severity: ERROR
   * Fix: "Confirm invoice date with vendor."

3. **HSN Format**

   * Rule: `hsn length in (4,6,8) and numeric`
   * Severity: WARNING
   * Fix: "Confirm HSN or map to correct product."

4. **Tax Calculation**

   * Rule: For each item: `tax_amount == round(qty * rate * tax_rate / 100, 2)`
   * Severity: ERROR
   * Fix: "Recompute tax or check item rates."

5. **Amounts Sum**

   * Rule: `sum(item.total) == total_amount` and `total_amount + tax_total == grand_total`
   * Severity: ERROR (or WARNING if discrepancy < 0.5%)
   * Fix: "Check rounding or missing items."

6. **Buyer GST (B2B mandatory)**

   * Rule: if invoice_type == B2B then buyer_gstin present and valid
   * Severity: ERROR
   * Fix: "Collect buyer GST."

7. **Vendor Registration Check**

   * Rule: call MCP->LLM / cached vendor DB to verify GSTIN active; if not active => WARNING/ERROR depending on policy.

8. **Duplicate Invoice Detection**

   * Rule: Match on supplier_gstin + invoice_number + invoice_date within sliding window (e.g., 90 days)
   * Severity: WARNING
   * Fix: "Possible duplicate — manual review."

9. **Currency / Decimal precision**

   * Rule: amounts are numeric, 2 decimal precision
   * Severity: ERROR

---

# 7) Report Generation Template (fields & sample JSON)

Report must be generated synchronously on validation completion. Minimal fields:

```json
{
  "report_id":"RPT-20251125-0001",
  "ingestion_id":"ING-20251125-0001",
  "validation_id":"VAL-0001",
  "status":"READY",
  "generated_at":"2025-11-25T09:35:00Z",
  "summary":{
    "status":"VALID",
    "errors":[],
    "warnings":[],
    "suggested_fixes":[]
  },
  "timeline":[
    {"agent":"ING-AG","action":"uploaded","ts":"2025-11-25T09:30:00Z"},
    {"agent":"OCR-AG","action":"extracted","ts":"2025-11-25T09:31:12Z"}
  ],
  "artifacts":{
    "tally_xml":"s3://artifacts/TXML-0001.xml",
    "zoho_json":"s3://artifacts/ZJSON-0001.json",
    "pdf_report":"s3://reports/RPT-0001.pdf"
  },
  "user_message":"Invoice validated and converted. Tally & Zoho artifacts available."
}
```

PDF generation: HTML template with header (company, ingestion id), sections (summary, errors, warnings, timeline, artifacts) and a footer with support contact.

---

# 8) Tally XML Example & Zoho JSON Example (from sample invoice)

### 8.1 Tally XML (artifact snippet `TXML-0001.xml`)

```xml
<ENVELOPE>
  <HEADER>
    <TALLYREQUEST>Import Data</TALLYREQUEST>
  </HEADER>
  <BODY>
    <IMPORTDATA>
      <REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC>
      <REQUESTDATA>
        <TALLYMESSAGE>
          <VOUCHER VCHTYPE="Sales" ACTION="Create">
            <DATE>20251101</DATE>
            <VOUCHERNUMBER>INV-1001</VOUCHERNUMBER>
            <PARTYNAME>TCS</PARTYNAME>
            <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
            <NARRATION>Invoice INV-1001</NARRATION>
            <ALLLEDGERENTRIES.LIST>
              <LEDGERNAME>Sales</LEDGERNAME>
              <AMOUNT>11800</AMOUNT>
            </ALLLEDGERENTRIES.LIST>
            <INVENTORYENTRIES.LIST>
              <STOCKITEMNAME>Service</STOCKITEMNAME>
              <RATE>10000</RATE>
              <AMOUNT>10000</AMOUNT>
              <BATCHALLOCATIONS.LIST>
                <ACTUALQTY>1</ACTUALQTY>
                <AMOUNT>10000</AMOUNT>
              </BATCHALLOCATIONS.LIST>
            </INVENTORYENTRIES.LIST>
          </VOUCHER>
        </TALLYMESSAGE>
      </REQUESTDATA>
    </IMPORTDATA>
  </BODY>
</ENVELOPE>
```

> Tally date format is `YYYYMMDD` (or `DDMMYYYY` depending on Tally version). Confirm Tally version and adjust date format and required fields (Ledger names, Inventory names).

### 8.2 Zoho Books JSON (artifact snippet `ZJSON-0001.json`)

```json
{
  "customer_id": "13546",
  "customer_name": "Corp Ltd",
  "invoice_number": "INV-1001",
  "date": "2025-11-01",
  "line_items": [
    {
      "name": "Service",
      "description": "Service",
      "quantity": 1,
      "rate": 10000,
      "hsn_or_sac": "9983",
      "taxes": [
        {
          "tax_name": "GST 18%",
          "tax_percentage": 18
        }
      ]
    }
  ],
  "sub_total": 10000,
  "tax_total": 1800,
  "total": 11800,
  "billing_address": {},
  "shipping_address": {}
}
```

> Zoho API requires `customer_id` (or contact) — system should map vendor/buyer to Zoho contacts or create them on-the-fly via Zoho API.

---

# 9) Implementation & deployment notes (practical tips)

* **Idempotency:** enforce `Idempotency-Key` on ingestion & conversion endpoints. Use unique `ingestion_id` to dedupe.
* **Orchestration:** Use LangGraph (orchestrator) to sequence gRPC calls. Validation agent must call `reports.generate` before acknowledging to orchestrator (recommended).
* **Message bus:** Use Kafka/RabbitMQ between agents for durability + gRPC for RPC control.
* **Storage:** store large artifacts (xml/json/pdf) in object storage (S3) and store URL in DB.
* **Retries:** integration agent should implement exponential backoff and update `integration_logs`.
* **Security:** REST JWT for users; service tokens for agents; gRPC mTLS + JWT metadata.
* **Monitoring:** export Prometheus metrics and push critical alarms to PagerDuty/Slack.
* **Testing:** unit tests for validation rules and end-to-end tests using sample invoice JSONs above.

---

# 10) Deliverable file list & next steps you can copy

* `openapi.yml` — Paste into Swagger Editor
* `agent_comm.proto` — gRPC A2A
* `mcp.proto` — gRPC MCP
* `db_schema.sql` — DDL + sample data
* `test_invoices.json` — Test payloads
* `tally_sample.xml` — sample Tally artifact
* `zoho_sample.json` — sample Zoho artifact

---

If you want, I can now (pick any or multiple):

A. Generate the **OpenAPI YAML as a downloadable file** and provide a link.
B. Produce **`protoc` command examples** and stub server/client code in Python or Go for the `agent_comm.proto` and `mcp.proto`.
C. Generate the **LangGraph node definitions** wiring the flow (start->OCR->Map->Validate->Report->Convert->Push).
D. Create **HTML template** for the PDF report (ready for wkhtmltopdf / WeasyPrint).
E. Build the **FastAPI skeleton** (controllers + pydantic models) for the REST Gateway.

Tell me which letters (A–E) you want me to produce immediately and I’ll output them in this chat.
