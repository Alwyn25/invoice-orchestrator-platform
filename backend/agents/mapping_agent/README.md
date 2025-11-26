# Mapping Agent

The **Mapping Agent** is a gRPC microservice responsible for transforming the raw, extracted schema from the OCR process into a normalized, canonical invoice schema.

## Responsibilities

- **Schema Normalization**: Applies rule-based logic to map fields from the `ocr_output` to the standard `mapped_schema`.
- **Data Enrichment**: (Future) Enriches the schema with data from external sources or LLM-based reasoning.
- **MCP Integration**:
  - Fetches `ocr_output` from the MCP.
  - Saves the normalized `mapped_schema` to the database via the MCP.
  - Emits metrics and audit events.

## API

- **gRPC Service**: `AgentComm`
- **RPC**: `MapSchema`
- **Port**: `6002`

## Configuration

| Environment Variable    | Description             | Default     |
| ----------------------- | ----------------------- | ----------- |
| `MCP_HOST`              | MCP service hostname    | `mcp`       |
| `MCP_PORT`              | MCP service port        | `50051`     |
| `LOG_LEVEL`             | Logging level           | `INFO`      |
