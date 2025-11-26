# Validation Agent

The **Validation Agent** is a gRPC microservice responsible for validating the normalized invoice schema against a set of predefined business rules.

## Responsibilities

- **Rule-Based Validation**: Executes a series of validation rules, such as:
  - GSTIN format validation.
  - Invoice date validation (not in the future).
  - HSN code format validation.
  - Basic tax and total amount calculations.
- **Anomaly Detection**: Flags invoices that require human review based on the severity and number of validation errors.
- **MCP Integration**:
  - Fetches the `mapped_schema` from the MCP.
  - Saves the validation results, including errors and warnings, to the `validation_logs` table via the MCP.
  - Emits metrics and audit events.

## API

- **gRPC Service**: `AgentComm`
- **RPC**: `ValidateSchema`
- **Port**: `6003`

## Configuration

| Environment Variable    | Description             | Default     |
| ----------------------- | ----------------------- | ----------- |
| `MCP_HOST`              | MCP service hostname    | `mcp`       |
| `MCP_PORT`              | MCP service port        | `50051`     |
| `LOG_LEVEL`             | Logging level           | `INFO`      |
