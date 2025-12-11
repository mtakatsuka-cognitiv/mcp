import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.conn = None

    def connect(self):
        """Establish a connection to the database."""
        if not self.conn or self.conn.closed:
            try:
                self.conn = psycopg2.connect(**self.db_config)
                # Enforce read-only session
                self.conn.set_session(readonly=True)
            except psycopg2.Error as e:
                logger.error(f"Error connecting to database: {e}")
                raise

    def close(self):
        """Close the database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def list_schemas(self) -> List[str]:
        """List all public schemas in the database."""
        self.connect()
        query = """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog') 
            AND schema_name NOT LIKE 'pg_toast%%' 
            AND schema_name NOT LIKE 'pg_temp%%'
            ORDER BY schema_name;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                return [row[0] for row in cur.fetchall()]
        except psycopg2.Error as e:
            logger.error(f"Error listing schemas: {e}")
            raise

    @staticmethod
    def validate_name(name: str, type_desc: str = "name"):
        """Validate a name (schema, table, etc.) to prevent potential issues."""
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            raise ValueError(f"Invalid {type_desc}: {name}")

    def list_tables(self, schema: str) -> List[str]:
        """List all tables in a given schema."""
        self.validate_name(schema, "schema name")

        self.connect()
        # Use parameterized query to prevent SQL injection
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (schema,))
                return [row[0] for row in cur.fetchall()]
        except psycopg2.Error as e:
            logger.error(f"Error listing tables in schema '{schema}': {e}")
            raise

    def describe_table(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """
        Get the table description (columns, types, etc.).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a column.
        """
        self.validate_name(schema, "schema name")
        self.validate_name(table, "table name")

        self.connect()
        query = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable, 
                column_default
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = %s
            ORDER BY ordinal_position;
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (schema, table))
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error describing table '{schema}.{table}': {e}")
            raise

    def get_table_indexes(self, schema: str, table: str) -> List[Dict[str, str]]:
        """
        Get the indexes for a table.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing index names and definitions.
        """
        self.validate_name(schema, "schema name")
        self.validate_name(table, "table name")

        self.connect()
        query = """
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = %s AND tablename = %s
            ORDER BY indexname;
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (schema, table))
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error getting indexes for table '{schema}.{table}': {e}")
            raise

    def get_table_constraints(self, schema: str, table: str) -> List[Dict[str, str]]:
        """
        Get the constraints for a table.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing constraint names and definitions.
        """
        self.validate_name(schema, "schema name")
        self.validate_name(table, "table name")

        self.connect()
        query = """
            SELECT conname as constraint_name, pg_get_constraintdef(c.oid) as constraint_def
            FROM pg_constraint c
            JOIN pg_namespace n ON n.oid = c.connamespace
            JOIN pg_class t ON t.oid = c.conrelid
            WHERE n.nspname = %s AND t.relname = %s
            ORDER BY conname;
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (schema, table))
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Error getting constraints for table '{schema}.{table}': {e}")
            raise
