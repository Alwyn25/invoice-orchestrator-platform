# Use Python 3.12 as the base image to maintain consistency
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency definitions
COPY pyproject.toml uv.lock* ./

# Install dependencies from the lockfile
RUN uv pip sync --no-cache-dir --system uv.lock

# Copy all necessary source code
COPY backend/ /app/backend/

# Set the Python path to the app root
ENV PYTHONPATH=/app

# Expose the agent's gRPC port
EXPOSE 6004

# Command to run the server
CMD ["python", "-m", "backend.agents.report_agent.server"]
