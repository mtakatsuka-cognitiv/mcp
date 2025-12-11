FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for cassandra-driver
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libev-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Install the package with dependencies
RUN pip install --no-cache-dir -e .

# Run the MCP server
CMD ["python", "-m", "scylladb_mcp"]
