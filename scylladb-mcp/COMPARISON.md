# ScyllaDB vs PostgreSQL MCP Comparison

This document shows how the ScyllaDB MCP implementation mirrors the PostgreSQL MCP structure.

## Directory Structure Comparison

### PostgreSQL MCP
```
postgresql-mcp/
├── src/postgresql_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   └── db.py
├── tests/test_db.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

### ScyllaDB MCP
```
scylladb-mcp/
├── src/scylladb_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   └── db.py
├── tests/test_db.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

✅ **Identical structure**

---

## MCP Tools Comparison

| PostgreSQL MCP | ScyllaDB MCP | Notes |
|----------------|--------------|-------|
| `list_schemas()` | `list_keyspaces()` | Organizational units |
| `list_tables(schema)` | `list_tables(keyspace)` | Tables in unit |
| `describe_table(schema, table)` | `describe_table(keyspace, table)` | Table schema |
| `get_table_indexes(schema, table)` | `get_table_indexes(keyspace, table)` | Indexes |
| `get_table_constraints(schema, table)` | `get_materialized_views(keyspace)` | Different features |

---

## Security Features Comparison

| Feature | PostgreSQL MCP | ScyllaDB MCP |
|---------|----------------|--------------|
| **Read-only enforcement** | `conn.set_session(readonly=True)` | By design (no write ops) |
| **Input validation** | Regex `^[a-zA-Z0-9_]+$` | ✅ Same pattern |
| **Parameterized queries** | ✅ Yes | ✅ Yes |
| **Authentication** | Required (USER, PASSWORD) | ✅ Optional |
| **Injection prevention** | ✅ Validated + parameterized | ✅ Validated + parameterized |

---

## Database Drivers

| Aspect | PostgreSQL | ScyllaDB |
|--------|-----------|----------|
| **Driver** | `psycopg2-binary` | `cassandra-driver` |
| **Connection** | Single connection | Cluster + session |
| **Result format** | RealDictCursor | Native dict rows |
| **Session mode** | `readonly=True` | N/A (enforced by design) |

---

## Key Implementation Adaptations

### PostgreSQL Uses Schemas
```python
# PostgreSQL
def list_schemas() -> List[str]:
    query = """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
    """
```

### ScyllaDB Uses Keyspaces
```python
# ScyllaDB
def list_keyspaces() -> List[str]:
    query = """
        SELECT keyspace_name 
        FROM system_schema.keyspaces 
        WHERE keyspace_name NOT IN ('system', 'system_schema', ...)
    """
```

---

### PostgreSQL Has Constraints
```python
# PostgreSQL
def get_table_constraints(schema: str, table: str):
    query = """
        SELECT conname as constraint_name, 
               pg_get_constraintdef(c.oid) as constraint_def
        FROM pg_constraint c
        ...
    """
```

### ScyllaDB Has Materialized Views
```python
# ScyllaDB
def get_materialized_views(keyspace: str):
    query = """
        SELECT view_name, base_table_name
        FROM system_schema.views 
        WHERE keyspace_name = %s
    """
```

---

### PostgreSQL Column Info
```python
# Returns: column_name, data_type, is_nullable, column_default
{
    "column_name": "id",
    "data_type": "integer",
    "is_nullable": "NO",
    "column_default": "nextval(...)"
}
```

### ScyllaDB Column Info (Enhanced)
```python
# Returns: column_name, type, kind, position
{
    "column_name": "id",
    "type": "uuid",
    "kind": "partition_key",  # or clustering, regular, static
    "position": 0
}
```

---

## Environment Variables

### PostgreSQL MCP
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=myuser          # Required
POSTGRES_PASSWORD=mypassword  # Required
POSTGRES_DATABASE=mydb        # Required
```

### ScyllaDB MCP
```bash
SCYLLA_HOST=localhost
SCYLLA_PORT=9042
SCYLLA_USER=myuser            # Optional
SCYLLA_PASSWORD=mypassword    # Optional
```

✅ **Key difference**: ScyllaDB authentication is optional (per user request)

---

## Docker Configuration

### PostgreSQL
```dockerfile
# Install system dependencies
RUN apt-get install -y libpq-dev

# Install driver
pip install psycopg2-binary
```

### ScyllaDB
```dockerfile
# Install system dependencies for cassandra-driver
RUN apt-get install -y gcc g++ libev-dev

# Install driver  
pip install cassandra-driver
```

---

## Testing Approach

Both implementations use **identical testing patterns**:

✅ Test valid name acceptance  
✅ Test invalid name rejection  
✅ Test validation in all methods  
✅ Mock-free, business logic validation  

### Example Test (Both)
```python
def test_validate_name_invalid():
    """Test that invalid names raise ValueError"""
    invalid_names = [
        "invalid;name",
        "name with spaces",
        "drop table faketable",
        "name--",
    ]
    
    for name in invalid_names:
        with pytest.raises(ValueError, match="Invalid name"):
            DatabaseManager.validate_name(name)
```

---

## Summary

The ScyllaDB MCP implementation:

✅ **Follows the same architecture** as PostgreSQL MCP  
✅ **Maintains security principles** (validation, parameterization, read-only)  
✅ **Adapts to ScyllaDB specifics** (keyspaces, partition keys, materialized views)  
✅ **Improves on authentication** (made optional per user feedback)  
✅ **Identical project structure** for consistency  
✅ **Same testing approach** for reliability  

Both servers provide a secure, read-only interface to their respective databases while following MCP best practices.
