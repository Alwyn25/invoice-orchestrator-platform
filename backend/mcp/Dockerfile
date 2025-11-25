# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the dependency lock file
COPY uv.lock .

# Install dependencies using the lock file
RUN uv pip sync --no-cache-dir --system uv.lock

# Copy the application code
COPY ./backend /app/backend

# Command to run the gRPC server
CMD ["uv", "run", "python", "-u", "backend/mcp/server.py"]
