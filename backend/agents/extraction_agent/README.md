# Extraction Agent

The **Extraction Agent** is a gRPC microservice responsible for performing Optical Character Recognition (OCR) on input documents (PDFs, images) to extract raw text and a structured schema of invoice fields.

## Responsibilities

- **OCR**: Converts document images to raw text using a cascading series of OCR engines (Tesseract, EasyOCR, etc.).
- **Schema Extraction**: Uses a Large Language Model (LLM) to extract a structured JSON schema from the raw OCR text.
- **MCP Integration**:
  - Fetches document bytes from the MCP service.
  - Saves the OCR output and extracted schema to the `ocr_output` table via the MCP.
  - Emits metrics and audit events to the MCP.

## API

- **gRPC Service**: `AgentComm`
- **RPC**: `StartOCR`
- **Port**: `6001`

## Configuration

| Environment Variable    | Description             | Default     |
| ----------------------- | ----------------------- | ----------- |
| `MCP_HOST`              | MCP service hostname    | `mcp`       |
| `MCP_PORT`              | MCP service port        | `50051`     |
| `LOG_LEVEL`             | Logging level           | `INFO`      |
