# Conversion Agent

The **Conversion Agent** is a gRPC microservice responsible for converting the validated invoice schema into formats required by external systems, such as Tally XML and Zoho JSON.

## Responsibilities

- **Format Conversion**: Transforms the canonical `mapped_schema` into specific XML or JSON formats.
- **MCP Integration**:
  - Fetches the `mapped_schema` and `validation_logs` from the MCP.
  - Saves the converted output to the `conversion_logs` table via the MCP.
  - Emits metrics and audit events.

## API

- **gRPC Service**: `AgentComm`
- **RPC**: `Convert`
- **Port**: `6005`

## Configuration

| Environment Variable    | Description             | Default     |
| ----------------------- | ----------------------- | ----------- |
| `MCP_HOST`              | MCP service hostname    | `mcp`       |
| `MCP_PORT`              | MCP service port        | `50051`     |
| `LOG_LEVEL`             | Logging level           | `INFO`      |
