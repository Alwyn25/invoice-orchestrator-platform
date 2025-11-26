# Report Agent

The **Report Agent** is a gRPC microservice responsible for generating a user-facing summary report of the invoice validation process.

## Responsibilities

- **Summary Generation**: Creates a JSON summary of the validation results, including errors, warnings, and suggested fixes.
- **Report Persistence**: (Future) Generates a PDF or HTML version of the report and saves it to a file storage service.
- **MCP Integration**:
  - Fetches `validation_logs` and `mapped_schema` from the MCP.
  - Saves the generated report summary to the `reports` table via the MCP.
  - Populates the `warnings_logs` table with itemized warnings.
  - Emits metrics and audit events.

## API

- **gRPC Service**: `AgentComm`
- **RPC**: `GenerateReport`
- **Port**: `6004`

## Configuration

| Environment Variable    | Description             | Default     |
| ----------------------- | ----------------------- | ----------- |
| `MCP_HOST`              | MCP service hostname    | `mcp`       |
| `MCP_PORT`              | MCP service port        | `50051`     |
| `LOG_LEVEL`             | Logging level           | `INFO`      |
