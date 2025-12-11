from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.cluster: Optional[Cluster] = None
        self.session: Optional[Session] = None

    def connect(self):
        """Establish a connection to the ScyllaDB cluster."""
        if not self.session or self.session.is_shutdown:
            try:
                contact_points = [self.db_config.get("host", "localhost")]
                port = int(self.db_config.get("port", "9042"))

                # Only use authentication if username and password are provided
                auth_provider = None
                if self.db_config.get("user") and self.db_config.get("password"):
                    auth_provider = PlainTextAuthProvider(
                        username=self.db_config["user"], password=self.db_config["password"]
                    )

                self.cluster = Cluster(
                    contact_points=contact_points, port=port, auth_provider=auth_provider
                )
                self.session = self.cluster.connect()

                # Note: ScyllaDB/Cassandra doesn't have a session-level read-only mode
                # Read-only enforcement is done by not providing write operations
                logger.info("Connected to ScyllaDB cluster")
            except Exception as e:
                logger.error(f"Error connecting to ScyllaDB: {e}")
                raise

    def close(self):
        """Close the database connection."""
        if self.session and not self.session.is_shutdown:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()

    def list_keyspaces(self) -> List[str]:
        """List all non-system keyspaces in the database."""
        self.connect()
        # Query system schema to get keyspaces, excluding system keyspaces
        query = """
            SELECT keyspace_name 
            FROM system_schema.keyspaces 
            WHERE keyspace_name NOT IN ('system', 'system_schema', 'system_auth', 
                                       'system_distributed', 'system_traces')
        """
        try:
            rows = self.session.execute(query)
            keyspaces = sorted([row.keyspace_name for row in rows])
            return keyspaces
        except Exception as e:
            logger.error(f"Error listing keyspaces: {e}")
            raise

    @staticmethod
    def validate_name(name: str, type_desc: str = "name"):
        """Validate a name (keyspace, table, etc.) to prevent SQL injection."""
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            raise ValueError(f"Invalid {type_desc}: {name}")

    def list_tables(self, keyspace: str) -> List[str]:
        """List all tables in a given keyspace."""
        self.validate_name(keyspace, "keyspace name")

        self.connect()
        # Use parameterized query to prevent SQL injection
        query = """
            SELECT table_name 
            FROM system_schema.tables 
            WHERE keyspace_name = %s
        """
        try:
            rows = self.session.execute(query, (keyspace,))
            tables = sorted([row.table_name for row in rows])
            return tables
        except Exception as e:
            logger.error(f"Error listing tables in keyspace '{keyspace}': {e}")
            raise

    def describe_table(self, keyspace: str, table: str) -> List[Dict[str, Any]]:
        """
        Get the table description (columns, types, etc.).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a column.
        """
        self.validate_name(keyspace, "keyspace name")
        self.validate_name(table, "table name")

        self.connect()
        query = """
            SELECT 
                column_name, 
                type,
                kind,
                position
            FROM system_schema.columns 
            WHERE keyspace_name = %s 
            AND table_name = %s
        """
        try:
            rows = self.session.execute(query, (keyspace, table))
            columns = []
            for row in rows:
                columns.append(
                    {
                        "column_name": row.column_name,
                        "type": row.type,
                        "kind": row.kind,  # partition_key, clustering, regular, static
                        "position": row.position,
                    }
                )
            # Sort by kind (partition keys first) and then by position
            columns.sort(
                key=lambda x: (
                    (
                        0
                        if x["kind"] == "partition_key"
                        else 1 if x["kind"] == "clustering" else 2 if x["kind"] == "static" else 3
                    ),
                    x["position"] if x["position"] is not None else 999,
                )
            )
            return columns
        except Exception as e:
            logger.error(f"Error describing table '{keyspace}.{table}': {e}")
            raise

    def get_table_indexes(self, keyspace: str, table: str) -> List[Dict[str, str]]:
        """
        Get the indexes for a table.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing index information.
        """
        self.validate_name(keyspace, "keyspace name")
        self.validate_name(table, "table name")

        self.connect()
        query = """
            SELECT 
                index_name,
                kind,
                options
            FROM system_schema.indexes 
            WHERE keyspace_name = %s AND table_name = %s
        """
        try:
            rows = self.session.execute(query, (keyspace, table))
            indexes = []
            for row in rows:
                indexes.append(
                    {
                        "index_name": row.index_name,
                        "kind": row.kind,
                        "options": str(row.options) if row.options else "",
                    }
                )
            return indexes
        except Exception as e:
            logger.error(f"Error getting indexes for table '{keyspace}.{table}': {e}")
            raise

    def get_materialized_views(self, keyspace: str) -> List[Dict[str, str]]:
        """
        Get materialized views in a keyspace.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing materialized view information.
        """
        self.validate_name(keyspace, "keyspace name")

        self.connect()
        query = """
            SELECT 
                view_name,
                base_table_name
            FROM system_schema.views 
            WHERE keyspace_name = %s
        """
        try:
            rows = self.session.execute(query, (keyspace,))
            views = []
            for row in rows:
                views.append({"view_name": row.view_name, "base_table_name": row.base_table_name})
            return sorted(views, key=lambda x: x["view_name"])
        except Exception as e:
            logger.error(f"Error getting materialized views in keyspace '{keyspace}': {e}")
            raise
