# Database MCP Servers

Model Context Protocol (MCP) servers for database schema exploration. These servers enable Claude to introspect your database structure through a secure, read-only interface.

## Available Servers

| Server | Description | Tools |
|--------|-------------|-------|
| **PostgreSQL MCP** | Schema exploration for PostgreSQL databases | `list_schemas`, `list_tables`, `describe_table`, `get_table_indexes`, `get_table_constraints` |
| **ScyllaDB MCP** | Schema exploration for ScyllaDB/Cassandra clusters | `list_keyspaces`, `list_tables`, `describe_table`, `get_table_indexes`, `get_materialized_views` |

## Prerequisites

- Docker
- Claude Desktop or Claude Code

## Quick Start

### 1. Create your environment file

Create a `.env` file in the MCP server directory with your database credentials:

**PostgreSQL** (`postgresql-mcp/.env`):
```
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=your_database
```

**ScyllaDB** (`scylladb-mcp/.env`):
```
SCYLLA_HOST=host.docker.internal
SCYLLA_PORT=9042
SCYLLA_USER=your_user
SCYLLA_PASSWORD=your_password
```

### 2. Configure Claude

Add to your Claude configuration file:

**Claude Desktop:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

**Claude Code:** `~/.claude/settings.json` or run `claude mcp add`

#### PostgreSQL

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker",
      "args": [
        "compose",
        "-f", "/path/to/postgresql-mcp/docker-compose.yml",
        "--env-file", "/path/to/postgresql-mcp/.env",
        "run", "--rm", "postgresql-mcp"
      ]
    }
  }
}
```

#### ScyllaDB

```json
{
  "mcpServers": {
    "scylladb": {
      "command": "docker",
      "args": [
        "compose",
        "-f", "/path/to/scylladb-mcp/docker-compose.yml",
        "--env-file", "/path/to/scylladb-mcp/.env",
        "run", "--rm", "scylladb-mcp"
      ]
    }
  }
}
```

### 3. Restart Claude

Restart Claude Desktop or Claude Code to load the new MCP server. The Docker image will be built automatically on first use.

## Environment Variables

### PostgreSQL MCP

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_HOST` | No | `localhost` | Database host |
| `POSTGRES_PORT` | No | `5432` | Database port |
| `POSTGRES_USER` | Yes | — | Database username |
| `POSTGRES_PASSWORD` | Yes | — | Database password |
| `POSTGRES_DATABASE` | Yes | — | Database name |

### ScyllaDB MCP

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SCYLLA_HOST` | No | `localhost` | Cluster host |
| `SCYLLA_PORT` | No | `9042` | CQL port |
| `SCYLLA_USER` | No | — | Username (if auth enabled) |
| `SCYLLA_PASSWORD` | No | — | Password (if auth enabled) |

## Network Configuration

**Local databases (macOS/Windows):** Use `host.docker.internal` as the host.

**Local databases (Linux):** Use `localhost` and add `network_mode: host` to the docker-compose.yml.

**Remote databases:** Use the actual hostname directly.

## Development

```bash
cd postgresql-mcp  # or scylladb-mcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## Security

These MCP servers are designed for read-only schema exploration. We recommend:

- Using database credentials with minimal required permissions
- Never committing credentials to version control

## License

Internal use only.
