# Company MCP Servers

A collection of Model Context Protocol (MCP) servers for internal use, containerized with Docker for easy deployment and dependency management.

## Available Servers

### PostgreSQL MCP
Located in `postgresql-mcp/`

Provides tools to interact with PostgreSQL databases, including table description and schema exploration capabilities.

## Prerequisites

- Docker Desktop installed and running
- Claude Desktop or Claude Code installed

## Project Structure

```
.
├── README.md
├── postgresql-mcp/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── src/
│       └── postgresql_mcp/
│           └── __init__.py
└── [future-mcp-servers]/
```

## Building MCP Servers

Each MCP server can be built as a Docker image:

```bash
# Build PostgreSQL MCP
cd postgresql-mcp
docker build -t company-postgresql-mcp .
```

## Configuration

### Claude Desktop Setup

1. Open your Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "host",
        "-e", "POSTGRES_HOST=localhost",
        "-e", "POSTGRES_PORT=5432",
        "-e", "POSTGRES_USER=your_user",
        "-e", "POSTGRES_PASSWORD=your_password",
        "-e", "POSTGRES_DATABASE=your_database",
        "company-postgresql-mcp"
      ]
    }
  }
}
```

3. Restart Claude Desktop for changes to take effect

### Claude Code Setup

1. Open your Claude Code settings file:
   - Location: `~/.config/claude-code/settings.json` (Linux/macOS)
   - Or use the command: `claude-code config edit`

2. Add the MCP server configuration under `mcpServers`:

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "host",
        "-e", "POSTGRES_HOST=localhost",
        "-e", "POSTGRES_PORT=5432",
        "-e", "POSTGRES_USER=your_user",
        "-e", "POSTGRES_PASSWORD=your_password",
        "-e", "POSTGRES_DATABASE=your_database",
        "company-postgresql-mcp"
      ]
    }
  }
}
```

3. Restart Claude Code or reload the configuration

## Environment Variables

Each MCP server may require specific environment variables. These are passed via Docker's `-e` flag:

### PostgreSQL MCP
- `POSTGRES_HOST`: Database host (default: localhost)
- `POSTGRES_PORT`: Database port (default: 5432)
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DATABASE`: Database name

## Networking Considerations

### Connecting to Local Databases

When connecting to databases running on your local machine from within Docker:

- Use `--network host` (Linux) to share the host's network
- On macOS/Windows, use `host.docker.internal` as the hostname instead of `localhost`

Example for macOS/Windows:
```json
{
  "args": [
    "run", "--rm", "-i",
    "-e", "POSTGRES_HOST=host.docker.internal",
    ...
  ]
}
```

### Connecting to Remote Databases

For remote databases, remove `--network host` and use the actual hostname:

```json
{
  "args": [
    "run", "--rm", "-i",
    "-e", "POSTGRES_HOST=db.example.com",
    "-e", "POSTGRES_PORT=5432",
    ...
  ]
}
```

## Development

### Adding a New MCP Server

1. Create a new directory for your MCP server
2. Copy the structure from an existing server (e.g., `postgresql-mcp/`)
3. Update `Dockerfile` and `pyproject.toml`
4. Implement your MCP server logic
5. Build and test the Docker image
6. Update this README with configuration instructions

### Testing MCP Servers

You can test an MCP server by running it directly:

```bash
docker run --rm -i \
  -e POSTGRES_HOST=localhost \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DATABASE=testdb \
  company-postgresql-mcp
```

The server should start and wait for MCP protocol messages on stdin.

## Troubleshooting

### Server Not Appearing in Claude

1. Verify the Docker image is built: `docker images | grep company-`
2. Check Claude's logs for errors:
   - Claude Desktop: Look in the app's developer console
   - Claude Code: Check the output panel
3. Ensure Docker Desktop is running
4. Verify the configuration file syntax is valid JSON

### Connection Issues

1. For local databases, ensure the database is running and accessible
2. Check network settings (use `host.docker.internal` on macOS/Windows)
3. Verify environment variables are correct
4. Test database connectivity outside of Docker first

### Docker Issues

1. Ensure Docker Desktop has sufficient resources
2. Check Docker logs: `docker logs <container-id>`
3. Verify the image builds successfully: `docker build -t test .`

## Security Notes

- Never commit passwords or sensitive credentials to version control
- Consider using Docker secrets or environment files for sensitive data
- Restrict database user permissions to only what's needed
- Use read-only database credentials when possible

## License

Internal use only.
