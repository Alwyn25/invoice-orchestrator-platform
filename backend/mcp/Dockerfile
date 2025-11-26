# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install uv for dependency management
RUN pip install uv

# Copy the dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv sync for reproducibility
RUN uv pip sync --no-cache-dir --system uv.lock

# Copy the application source code
# We need docs/proto for gRPC imports to work correctly
COPY backend/ ./backend/
COPY docs/proto/ ./docs/proto/

# Expose the gRPC port
EXPOSE 50051

# Command to run the gRPC server
# Using -m ensures that the package is run as a module, making relative imports work
CMD ["python", "-m", "backend.mcp.server"]
