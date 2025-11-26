# API Documentation

This document provides a detailed overview of the REST and gRPC APIs for the Invoice Orchestrator Platform.

## Gateway REST API

The Gateway is the single entry point for all HTTP traffic. It exposes a REST API for interacting with the system.

**Base URL**: `http://localhost:8000`

### Endpoints

- **`POST /ingestion/upload`**: Uploads an invoice for processing.
- **`POST /orchestrate/{ingestion_id}`**: Starts the orchestration workflow for a given ingestion ID.
- **`GET /orchestrations/{ingestion_id}`**: Retrieves the current state of an orchestration.
- **`POST /human-review/{ingestion_id}/resolve`**: Resolves a pending human review.
- **`GET /metrics/dashboard`**: Retrieves dashboard metrics.
- **`POST /reports/generate`**: Generates a report for a given validation ID.
- **`POST /convert/tally`**: Converts a validated invoice to Tally XML.
- **`POST /convert/zoho`**: Converts a validated invoice to Zoho JSON.
- **`POST /integration/push`**: Pushes a converted invoice to an external platform.
- **`GET /warnings`**: Retrieves warnings for a given ingestion or validation ID.

For detailed request and response schemas, please refer to the auto-generated Swagger documentation at `http://localhost:8000/docs`.

## gRPC APIs

The system uses gRPC for inter-service communication. The Protobuf definitions for all gRPC services are located in the `docs/proto` directory.

### MCP Service

- **Proto file**: `docs/proto/mcp.proto`
- **Service**: `MCP`
- **Port**: `50051`

### Agent Services

- **Proto file**: `docs/proto/agent_comm.proto`
- **Service**: `AgentComm`
- **Ports**: `6001`-`6006`
