# Integration Agent

The **Integration Agent** is a gRPC microservice responsible for pushing the converted invoice data to external platforms like Tally and Zoho.

## Responsibilities

- **External API Integration**: Makes HTTP POST requests to the configured endpoints for Tally and Zoho.
- **Retry Logic**: Implements a basic retry policy for failed integration attempts.
- **MCP Integration**:
  - Fetches the converted output from the `conversion_logs` table via the MCP.
  - Saves the integration results, including platform responses and status codes, to the `integration_logs` table via the MCP.
  - Emits metrics and audit events.

## API

- **gRPC Service**: `AgentComm`
- **RPC**: `PushIntegration`
- **Port**: `6006`

## Configuration

| Environment Variable    | Description                | Default                        |
| ----------------------- | -------------------------- | ------------------------------ |
| `MCP_HOST`              | MCP service hostname       | `mcp`                          |
| `MCP_PORT`              | MCP service port           | `50051`                        |
| `LOG_LEVEL`             | Logging level              | `INFO`                         |
| `TALLY_URL`             | Tally integration endpoint | `http://localhost:9000`        |
| `ZOHO_BASE_URL`         | Zoho API base URL          | `https://books.zoho.com/api/v3` |
| `ZOHO_TOKEN`            | Zoho API OAuth token       | (not set)                      |
