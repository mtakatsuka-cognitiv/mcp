"""Main entry point for ScyllaDB MCP Server"""

import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Generator
from mcp.server.fastmcp import FastMCP
from scylladb_mcp.db import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_config() -> dict[str, str]:
    """Get database configuration from environment variables"""
    config = {
        "host": os.getenv("SCYLLA_HOST", "localhost"),
        "port": os.getenv("SCYLLA_PORT", "9042"),
    }

    # Add optional authentication if provided
    user = os.getenv("SCYLLA_USER", "")
    password = os.getenv("SCYLLA_PASSWORD", "")

    if user:
        config["user"] = user
    if password:
        config["password"] = password

    return config


@contextmanager
def get_db() -> Generator[DatabaseManager, None, None]:
    """Context manager for DatabaseManager"""
    db_config = get_db_config()

    db = DatabaseManager(db_config)
    try:
        yield db
    finally:
        db.close()


# Initialize FastMCP server
mcp = FastMCP("scylladb")


@mcp.tool()
def list_keyspaces() -> list[str]:
    """
    List all non-system keyspaces in the ScyllaDB cluster.

    Returns:
        list[str]: A list of keyspace names.
    """
    with get_db() as db:
        return db.list_keyspaces()


@mcp.tool()
def list_tables(keyspace: str) -> list[str]:
    """
    List all tables in a given keyspace.

    Args:
        keyspace: The name of the keyspace to list tables from.

    Returns:
        list[str]: A list of table names in the specified keyspace.
    """
    with get_db() as db:
        return db.list_tables(keyspace)


@mcp.tool()
def describe_table(keyspace: str, table: str) -> List[Dict[str, Any]]:
    """
    Get the table description (columns, types, key information, etc.).

    Args:
        keyspace: The name of the keyspace.
        table: The name of the table.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a column with its type and kind.
    """
    with get_db() as db:
        return db.describe_table(keyspace, table)


@mcp.tool()
def get_table_indexes(keyspace: str, table: str) -> List[Dict[str, str]]:
    """
    Get the secondary indexes for a table.

    Args:
        keyspace: The name of the keyspace.
        table: The name of the table.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing index information.
    """
    with get_db() as db:
        return db.get_table_indexes(keyspace, table)


@mcp.tool()
def get_materialized_views(keyspace: str) -> List[Dict[str, str]]:
    """
    Get the materialized views in a keyspace.

    Args:
        keyspace: The name of the keyspace.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing materialized view information.
    """
    with get_db() as db:
        return db.get_materialized_views(keyspace)


def main():
    """Main entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
