# PostgreSQL MCP Server

An MCP (Model Context Protocol) server that provides tools for interacting with PostgreSQL databases.

## Features

Once implemented, this MCP server will provide:

- `describe_table`: Get detailed schema information for a specific table
- `list_tables`: List all tables in the database
- `list_schemas`: List all schemas in the database
- `get_table_columns`: Get column information for a table
- Additional PostgreSQL introspection capabilities

## Building the Docker Image

```bash
cd postgresql-mcp
docker build -t company-postgresql-mcp .
```

## Running Locally (for testing)

```bash
docker run --rm -i \
  --network host \
  -e POSTGRES_HOST=localhost \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DATABASE=your_database \
  company-postgresql-mcp
```

For macOS/Windows, replace `--network host` with the hostname:
```bash
docker run --rm -i \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DATABASE=your_database \
  company-postgresql-mcp
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_HOST` | No | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | No | `5432` | PostgreSQL port |
| `POSTGRES_USER` | Yes | - | Database username |
| `POSTGRES_PASSWORD` | Yes | - | Database password |
| `POSTGRES_DATABASE` | Yes | - | Database name |

## Configuration with Claude

See the main [README.md](../README.md) for detailed instructions on configuring this MCP server with Claude Desktop and Claude Code.

Quick example for Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--network", "host",
        "-e", "POSTGRES_HOST=localhost",
        "-e", "POSTGRES_PORT=5432",
        "-e", "POSTGRES_USER=myuser",
        "-e", "POSTGRES_PASSWORD=mypassword",
        "-e", "POSTGRES_DATABASE=mydb",
        "company-postgresql-mcp"
      ]
    }
  }
}
```

## Development

### Project Structure

```
postgresql-mcp/
├── Dockerfile
├── README.md
├── pyproject.toml
└── src/
    └── postgresql_mcp/
        ├── __init__.py
        └── __main__.py
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
   export POSTGRES_HOST=localhost
   export POSTGRES_USER=myuser
   export POSTGRES_PASSWORD=mypassword
   export POSTGRES_DATABASE=mydb
   ```

4. Run the server:
   ```bash
   python -m postgresql_mcp
   ```

### Adding New Tools

To add new MCP tools:

1. Define the tool schema in the MCP server initialization
2. Implement the tool handler function
3. Register the tool with the MCP server
4. Update this README with the new tool's documentation

## Security Considerations

- Use read-only database credentials when possible
- Limit database user permissions to only required schemas/tables
- Never commit credentials to version control
- Consider using connection pooling for production deployments
- Validate and sanitize all user inputs

## Troubleshooting

### Cannot connect to database

1. Verify PostgreSQL is running: `pg_isready -h localhost`
2. Check credentials are correct
3. Ensure network connectivity (use `host.docker.internal` on macOS/Windows)
4. Verify firewall rules allow connections

### Server not responding

1. Check Docker container logs: `docker ps` then `docker logs <container-id>`
2. Verify environment variables are set correctly
3. Ensure the Docker image is built with latest code: `docker build -t company-postgresql-mcp .`

## Future Enhancements

- Connection pooling for better performance
- Support for multiple database connections
- Query execution capabilities (with safety controls)
- Schema migration detection
- Table relationship visualization
- Performance metrics and query statistics
