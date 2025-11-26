# Invoice Orchestrator Platform

AI-powered end-to-end invoice ingestion, validation, conversion, and posting system with multi-agent orchestration and human-in-the-loop review.

## Architecture

![Architecture](docs/architecture/workflow_diagram.png)

## Key Features

- **Multi-agent architecture**: extraction, mapping, validation, report, conversion, integration
- **LangGraph orchestrated workflow**: A stateful, resilient, and observable workflow engine.
- **Human-in-the-loop**: Anomaly review and manual intervention capabilities.
- **FastAPI REST gateway**: A single entry point for all HTTP traffic.
- **MCP-backed DB + LLM access**: A central service for data persistence and language model access.
- **Full audit logging + metrics collection**: Comprehensive observability into the system.
- **Tally XML + Zoho JSON conversion modules**: Extensible modules for converting to various formats.
- **Dockerized microservices**: All services are containerized for easy deployment and scaling.

## Repository Structure

```
.
├── backend/
│   ├── gateway/
│   ├── mcp/
│   ├── agents/
│   ├── orchestrator/
│   └── tests/
├── frontend/
│   └── dashboard/
├── docs/
│   ├── proto/
│   └── db/
└── docker-compose.yml
```

## Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 18+ (for frontend)
- `uv` (or `pip` and `venv`)
- gRPC tools (`grpcio-tools`)
- Postgres client (optional)

## How to Run (Local Development)

### Clone & Install

```bash
git clone https://github.com/your-org/invoice-orchestrator-platform.git
cd invoice-orchestrator-platform
```

### Start services with docker-compose

```bash
docker-compose up --build
```

After that, the services will be available at:

- **Gateway**: http://localhost:8000/docs
- **Orchestrator**: http://localhost:8100/health
- **Dashboard UI**: http://localhost:3000
- **MCP gRPC**: `localhost:50051`
- **Agents**: ports `6001`–`6006`

## Development Guide

### Backend Setup (Local)

```bash
cd backend
python -m venv venv
source venv/bin/activate
uv pip install -r requirements.txt
```

### Run Gateway Locally

```bash
uvicorn backend.gateway.app.main:app --reload --port 8000
```

### Generate gRPC stubs

```bash
python -m grpc_tools.protoc \
  -I docs/proto \
  --python_out=backend/shared/grpc \
  --grpc_python_out=backend/shared/grpc \
  docs/proto/*.proto
```

## Environment Variables

| Variable                  | Description                | Default                |
| ------------------------- | -------------------------- | ---------------------- |
| `DATABASE_URL`            | Postgres URI               | `postgres://...`       |
| `MCP_HOST`                | MCP hostname               | `mcp`                  |
| `EXTRACTION_AGENT_PORT`   | Extraction agent port      | `6001`                 |
| `VALIDATION_AGENT_PORT`   | Validation agent port      | `6003`                 |
| ...                       | ...                        | ...                    |

## API Documentation

- **Gateway REST Docs**: http://localhost:8000/docs
- **Orchestrator Docs**: http://localhost:8100/docs
- **Protobuf files**: [docs/proto/](docs/proto/)

## Workflow Overview

1.  **Ingestion** → **OCR** → **Mapping** → **Validation**
2.  **Human Review** (optional)
3.  **Report Generation**
4.  **Conversion** to Tally XML / Zoho JSON
5.  **Integration**: Push to platforms
6.  **Metrics + Audit** logging

## Human-in-the-loop Review

Anomalies are flagged during the validation step. If an invoice requires manual review, the orchestration is paused, and the status is set to `PENDING_REVIEW`. The review can be resolved via the orchestrator's API:

- `POST /human-review/{ingestion_id}/resolve`

## Testing Instructions

```bash
pytest backend
```

- **Unit tests**: `tests/unit`
- **Integration tests**: `tests/integration`
- **E2E tests**: `tests/e2e`

## Deployment Guide

- **Docker Compose**: `docker-compose up -d`
- **Kubernetes**: Manifests are available under `infra/k8s/`. Apply them with `kubectl apply -f infra/k8s/`.
- **CI/CD**: The GitHub Actions workflow in `.github/workflows/ci.yml` will automatically run tests and build Docker images.

## Troubleshooting

- **Ports in use**: Make sure no other services are running on ports `8000`, `8100`, `50051`, or `6001`-`6006`.
- **gRPC stub mismatch**: Regenerate the stubs with the command in the Development Guide.
- **Postgres auth**: Check the `DATABASE_URL` environment variable.
- **Missing environment variables**: Make sure all required environment variables are set.

## Contributing

Please see the `CONTRIBUTING.md` file for details.

## License

This project is licensed under the MIT License.

## Maintainers & Contact

- **Backend**: Jules
- **Frontend**: (to be assigned)
- **DevOps**: (to be assigned)
