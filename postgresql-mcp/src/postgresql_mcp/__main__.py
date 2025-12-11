"""Main entry point for PostgreSQL MCP Server"""

import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Generator
from mcp.server.fastmcp import FastMCP
from postgresql_mcp.db import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_config() -> dict[str, str]:
    """Get database configuration from environment variables"""
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", ""),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "database": os.getenv("POSTGRES_DATABASE", ""),
    }


@contextmanager
def get_db() -> Generator[DatabaseManager, None, None]:
    """Context manager for DatabaseManager"""
    db_config = get_db_config()
    if not db_config["user"] or not db_config["password"] or not db_config["database"]:
        raise ValueError(
            "Database credentials (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE) are required"
        )

    db = DatabaseManager(db_config)
    try:
        yield db
    finally:
        db.close()


# Initialize FastMCP server
mcp = FastMCP("postgresql")


@mcp.tool()
def list_schemas() -> list[str]:
    """
    List all public schemas in the database.

    Returns:
        list[str]: A list of schema names.
    """
    with get_db() as db:
        return db.list_schemas()


@mcp.tool()
def list_tables(schema: str) -> list[str]:
    """
    List all tables in a given schema.

    Args:
        schema: The name of the schema to list tables from.

    Returns:
        list[str]: A list of table names in the specified schema.
    """
    with get_db() as db:
        return db.list_tables(schema)


@mcp.tool()
def describe_table(schema: str, table: str) -> List[Dict[str, Any]]:
    """
    Get the table description (columns, types, etc.).

    Args:
        schema: The name of the schema.
        table: The name of the table.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a column.
    """
    with get_db() as db:
        return db.describe_table(schema, table)


@mcp.tool()
def get_table_indexes(schema: str, table: str) -> List[Dict[str, str]]:
    """
    Get the indexes for a table.

    Args:
        schema: The name of the schema.
        table: The name of the table.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing index names and definitions.
    """
    with get_db() as db:
        return db.get_table_indexes(schema, table)


@mcp.tool()
def get_table_constraints(schema: str, table: str) -> List[Dict[str, str]]:
    """
    Get the constraints for a table (primary keys, foreign keys, unique constraints).

    Args:
        schema: The name of the schema.
        table: The name of the table.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing constraint names and definitions.
    """
    with get_db() as db:
        return db.get_table_constraints(schema, table)


def main():
    """Main entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
