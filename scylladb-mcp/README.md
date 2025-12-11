# ScyllaDB MCP Server

An MCP (Model Context Protocol) server that provides tools for interacting with ScyllaDB databases.

## Features

This MCP server provides the following tools:

- `list_keyspaces`: List all non-system keyspaces in the ScyllaDB cluster
- `list_tables`: List all tables in a specific keyspace
- `describe_table`: Get detailed schema information for a specific table (columns, types, partition keys, clustering keys)
- `get_table_indexes`: Get secondary indexes for a table
- `get_materialized_views`: List materialized views in a keyspace

## Security Features

- **Read-only operations**: Only SELECT queries are exposed; no write operations available
- **Input validation**: All keyspace and table names are validated using regex to prevent SQL injection
- **Parameterized queries**: All queries use parameterized statements
- **Optional authentication**: Supports ScyllaDB clusters with or without authentication

## Building the Docker Image

```bash
cd scylladb-mcp
docker build -t scylladb-mcp .
```

## Running Locally (for testing)

### With Docker Compose (Recommended for Testing)

The easiest way to test is using the included docker-compose configuration:

```bash
docker-compose up
```

This will start both a ScyllaDB test cluster and the MCP server.

### Standalone Docker Run

```bash
docker run --rm -i \
  --network host \
  -e SCYLLA_HOST=localhost \
  -e SCYLLA_PORT=9042 \
  scylladb-mcp
```

For macOS/Windows (when ScyllaDB is on host):
```bash
docker run --rm -i \
  -e SCYLLA_HOST=host.docker.internal \
  -e SCYLLA_PORT=9042 \
  scylladb-mcp
```

### With Authentication

If your ScyllaDB cluster requires authentication:

```bash
docker run --rm -i \
  --network host \
  -e SCYLLA_HOST=localhost \
  -e SCYLLA_PORT=9042 \
  -e SCYLLA_USER=your_user \
  -e SCYLLA_PASSWORD=your_password \
  scylladb-mcp
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SCYLLA_HOST` | No | `localhost` | ScyllaDB host address |
| `SCYLLA_PORT` | No | `9042` | ScyllaDB CQL port |
| `SCYLLA_USER` | No | - | Username (only if authentication is enabled) |
| `SCYLLA_PASSWORD` | No | - | Password (only if authentication is enabled) |

## Configuration with Claude

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "scylladb": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--network", "host",
        "-e", "SCYLLA_HOST=localhost",
        "-e", "SCYLLA_PORT=9042",
        "scylladb-mcp"
      ]
    }
  }
}
```

With authentication:
```json
{
  "mcpServers": {
    "scylladb": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--network", "host",
        "-e", "SCYLLA_HOST=localhost",
        "-e", "SCYLLA_PORT=9042",
        "-e", "SCYLLA_USER=myuser",
        "-e", "SCYLLA_PASSWORD=mypassword",
        "scylladb-mcp"
      ]
    }
  }
}
```

### Claude Code

Similar configuration can be used for Claude Code CLI.

## Development

### Project Structure

```
scylladb-mcp/
├── Dockerfile
├── docker-compose.yml
├── README.md
├── pyproject.toml
├── src/
│   └── scylladb_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       └── db.py
└── tests/
    └── test_db.py
```

### Local Development (without Docker)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set environment variables:
   ```bash
   export SCYLLA_HOST=localhost
   export SCYLLA_PORT=9042
   # Optional: if authentication is enabled
   # export SCYLLA_USER=myuser
   # export SCYLLA_PASSWORD=mypassword
   ```

4. Run the server:
   ```bash
   python -m scylladb_mcp
   ```

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

## ScyllaDB vs PostgreSQL Differences

If you're familiar with the PostgreSQL MCP server, here are the key differences:

| PostgreSQL | ScyllaDB |
|------------|----------|
| Schemas | Keyspaces |
| `list_schemas()` | `list_keyspaces()` |
| Constraints | Not applicable (no foreign keys in ScyllaDB) |
| `get_table_constraints()` | N/A |
| Indexes | Secondary indexes (limited) |
| N/A | `get_materialized_views()` |

ScyllaDB uses a different data model:
- **Partition keys**: Determine data distribution across nodes
- **Clustering keys**: Determine sort order within a partition
- **Regular columns**: Standard data columns
- **Static columns**: Shared across rows with same partition key

## Security Considerations

- **Read-only by design**: This MCP server only exposes read operations
- **No write operations**: No INSERT, UPDATE, DELETE, or DDL operations are available
- **Input validation**: All user inputs are validated with strict regex patterns
- **Parameterized queries**: All CQL queries use parameterized statements to prevent injection
- **Optional authentication**: Use authentication credentials if your cluster requires it
- **Limited user permissions**: Consider using a restricted ScyllaDB role with minimal permissions

## Troubleshooting

### Cannot connect to ScyllaDB

1. Verify ScyllaDB is running: `docker ps` or check your cluster status
2. Test connectivity: `cqlsh <host> <port>`
3. Check authentication settings if enabled
4. For Docker Desktop on macOS/Windows, use `host.docker.internal` instead of `localhost`
5. Verify firewall rules allow connections on port 9042

### Server not responding

1. Check Docker container logs: `docker ps` then `docker logs <container-id>`
2. Verify environment variables are set correctly
3. Ensure the Docker image is built with latest code: `docker build -t scylladb-mcp .`
4. Check ScyllaDB is actually ready: `docker-compose logs scylladb`

### Authentication errors

1. Verify `SCYLLA_USER` and `SCYLLA_PASSWORD` are set if authentication is enabled
2. Check that the user has permission to query system tables
3. If authentication is NOT enabled, leave username and password empty

## Example Usage

Once connected through Claude, you can use natural language:

- "List all keyspaces in the ScyllaDB cluster"
- "Show me all tables in the user_data keyspace"
- "Describe the schema for the users table in the user_data keyspace"
- "What indexes exist on the events table?"
- "Show me the materialized views in the analytics keyspace"

## Future Enhancements

- Connection pooling for better performance
- Support for multiple clusters
- Table compaction strategy information
- Replication strategy details
- Token range and partition distribution information
- CQL query execution (with strict safety controls)
