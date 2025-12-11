# Docker Setup Guide

This guide explains how to run the PostgreSQL MCP server in Docker and connect it to Claude Desktop.

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and update it with your database credentials:

```bash
cp .env.example .env
```

Edit `.env` and set your PostgreSQL connection details:
- `POSTGRES_HOST`: Use `host.docker.internal` to connect to your host machine's PostgreSQL, or `postgres` to use the local PostgreSQL service
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_USER`: Your PostgreSQL username
- `POSTGRES_PASSWORD`: Your PostgreSQL password
- `POSTGRES_DATABASE`: The database name to connect to

### 2. Build and Run with Docker Compose

#### Option A: Connect to External PostgreSQL (on your host machine)

```bash
# Build and start the MCP server
docker-compose up -d postgresql-mcp

# View logs
docker-compose logs -f postgresql-mcp

# Stop the server
docker-compose down
```

#### Option B: Run with Local PostgreSQL Database

If you want to test with a local PostgreSQL instance, uncomment the `postgres` service in `docker-compose.yml`:

1. Uncomment the `postgres` service section
2. Uncomment the `depends_on` section in `postgresql-mcp`
3. Uncomment the `volumes` section at the bottom
4. Update `POSTGRES_HOST=postgres` in your `.env` file

Then run:

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### 3. Configure Claude Desktop

Add the following to your Claude Desktop configuration:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker-compose",
      "args": [
        "-f",
        "/Users/marktakatsuka/GH/mcp-testing/postgresql-mcp/docker-compose.yml",
        "run",
        "--rm",
        "postgresql-mcp"
      ],
      "env": {
        "POSTGRES_HOST": "host.docker.internal",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "your_username",
        "POSTGRES_PASSWORD": "your_password",
        "POSTGRES_DATABASE": "your_database"
      }
    }
  }
}
```

**Important:** Replace the environment variables with your actual database credentials, or use the `--env-file` flag to load from `.env`.

### Alternative: Using Environment File in Claude Config

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "docker-compose",
      "args": [
        "-f",
        "/Users/marktakatsuka/GH/mcp-testing/postgresql-mcp/docker-compose.yml",
        "--env-file",
        "/Users/marktakatsuka/GH/mcp-testing/postgresql-mcp/.env",
        "run",
        "--rm",
        "postgresql-mcp"
      ]
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop for the changes to take effect.

## Testing the Connection

You can test the MCP server directly using Docker:

```bash
# Run interactively and see output
docker-compose run --rm postgresql-mcp
```

## Troubleshooting

### Cannot connect to host PostgreSQL

If you're having trouble connecting to PostgreSQL on your host machine:

1. **Check PostgreSQL is accepting connections:**
   ```bash
   psql -h localhost -U your_username -d your_database
   ```

2. **Verify PostgreSQL allows connections from Docker:**
   - Check `postgresql.conf`: `listen_addresses = '*'` or `'localhost'`
   - Check `pg_hba.conf`: Add entry for Docker network if needed

3. **Use the correct host:**
   - macOS/Windows: `host.docker.internal`
   - Linux: Use `--network=host` or the host's IP address

### View MCP Server Logs

```bash
docker-compose logs -f postgresql-mcp
```

### Rebuild After Code Changes

```bash
docker-compose build postgresql-mcp
docker-compose up -d postgresql-mcp
```

## Security Notes

- **Never commit `.env` files** with real credentials to version control
- The `.env` file is already in `.gitignore`
- For production use, consider using Docker secrets or a secure credential management system
- The MCP server runs in read-only mode and cannot modify your database

## Advanced Configuration

### Custom Network Configuration

If you need to connect to PostgreSQL in another Docker network:

```yaml
networks:
  mcp-network:
    external: true
    name: your-existing-network
```

### Volume Mounts for Development

To avoid rebuilding the image during development, you can mount your source code:

```yaml
volumes:
  - ./src:/app/src
```
