# PostgreSQL MCP Server (C#)

A C# implementation of an MCP (Model Context Protocol) server that provides tools for interacting with PostgreSQL databases.

## Features

This MCP server provides the following tools:

- `list_schemas`: List all public schemas in the database
- `list_tables`: List all tables in a given schema
- `describe_table`: Get detailed schema information for a specific table (columns, types, nullability, defaults)
- `get_table_indexes`: Get index information for a table
- `get_table_constraints`: Get constraints for a table (primary keys, foreign keys, unique constraints)

## Building the Docker Image

```bash
cd postgresql-cs-mcp
docker build -t postgresql-cs-mcp .
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
  postgresql-cs-mcp
```

For macOS/Windows, replace `--network host` with the hostname:
```bash
docker run --rm -i \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DATABASE=your_database \
  postgresql-cs-mcp
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
    "postgresql-cs": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "--network", "host",
        "-e", "POSTGRES_HOST=localhost",
        "-e", "POSTGRES_PORT=5432",
        "-e", "POSTGRES_USER=myuser",
        "-e", "POSTGRES_PASSWORD=mypassword",
        "-e", "POSTGRES_DATABASE=mydb",
        "postgresql-cs-mcp"
      ]
    }
  }
}
```

## Development

### Project Structure

```
postgresql-cs-mcp/
├── Dockerfile
├── .dockerignore
├── README.md
├── Cognitiv.PostgresqlMcp.sln
└── src/
    └── PostgresqlMcp/
        ├── PostgresqlMcp.csproj
        ├── Program.cs
        ├── PostgresqlTools.cs
        └── DatabaseManager.cs
```

### Local Development (without Docker)

1. Ensure .NET 8.0 SDK is installed

2. Restore dependencies:
   ```bash
   cd postgresql-cs-mcp
   dotnet restore
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
   dotnet run --project src/PostgresqlMcp
   ```

### Building

```bash
dotnet build
```

### Publishing

```bash
dotnet publish -c Release
```

## Architecture

- **Program.cs**: Entry point that initializes the MCP server using `Microsoft.Extensions.Hosting` and configures the stdio transport.
- **PostgresqlTools.cs**: Contains MCP tool definitions using the `[McpServerTool]` attribute.
- **DatabaseManager.cs**: Handles all PostgreSQL database operations using Npgsql.

### Key Dependencies

- `ModelContextProtocol` - Official .NET MCP SDK
- `Npgsql` - PostgreSQL driver for .NET
- `Microsoft.Extensions.Hosting` - Host builder for dependency injection and logging

## Security Considerations

- The database connection uses parameterized queries to prevent SQL injection
- Input validation using regex ensures only valid schema/table names are accepted
- Use read-only database credentials when possible
- Limit database user permissions to only required schemas/tables
- Never commit credentials to version control
- Consider using connection pooling for production deployments

## Troubleshooting

### Cannot connect to database

1. Verify PostgreSQL is running: `pg_isready -h localhost`
2. Check credentials are correct
3. Ensure network connectivity (use `host.docker.internal` on macOS/Windows)
4. Verify firewall rules allow connections

### Server not responding

1. Check Docker container logs: `docker ps` then `docker logs <container-id>`
2. Verify environment variables are set correctly
3. Ensure the Docker image is built with latest code: `docker build -t postgresql-cs-mcp .`

### Build errors

1. Ensure .NET 8.0 SDK is installed: `dotnet --version`
2. Clear NuGet cache: `dotnet nuget locals all --clear`
3. Restore packages: `dotnet restore`
