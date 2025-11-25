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

# Expose the gateway's HTTP port
EXPOSE 8000

# Command to run the uvicorn server
CMD ["uvicorn", "backend.gateway.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
