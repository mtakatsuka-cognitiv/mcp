import pytest
from scylladb_mcp.db import DatabaseManager


@pytest.fixture
def db_manager():
    return DatabaseManager({})


def test_validate_name_valid():
    """Test that valid names pass validation"""
    valid_names = [
        "my_keyspace",
        "keyspace123",
        "UPPERCASE",
        "_hidden",
        "users",
        "user_profiles",
        "table123",
        "test_table",
    ]
    for name in valid_names:
        # Should not raise exception
        DatabaseManager.validate_name(name)


def test_validate_name_invalid():
    """Test that invalid names raise ValueError"""
    invalid_names = [
        "invalid;name",
        "name with spaces",
        "drop table faketable",
        "name--",
        "name/*",
        "name.table",
        "name'or'1=1",
        "name--comment",
    ]

    for name in invalid_names:
        with pytest.raises(ValueError, match="Invalid name"):
            DatabaseManager.validate_name(name)


def test_list_tables_validation(db_manager):
    """Test that list_tables validates keyspace name"""
    with pytest.raises(ValueError, match="Invalid keyspace name"):
        db_manager.list_tables("invalid;keyspace")


def test_describe_table_validation(db_manager):
    """Test that describe_table validates keyspace and table names"""
    with pytest.raises(ValueError, match="Invalid keyspace name"):
        db_manager.describe_table("invalid;keyspace", "valid_table")

    with pytest.raises(ValueError, match="Invalid table name"):
        db_manager.describe_table("my_keyspace", "invalid;table")


def test_get_table_indexes_validation(db_manager):
    """Test that get_table_indexes validates keyspace and table names"""
    with pytest.raises(ValueError, match="Invalid keyspace name"):
        db_manager.get_table_indexes("invalid;keyspace", "valid_table")

    with pytest.raises(ValueError, match="Invalid table name"):
        db_manager.get_table_indexes("my_keyspace", "invalid;table")


def test_get_materialized_views_validation(db_manager):
    """Test that get_materialized_views validates keyspace name"""
    with pytest.raises(ValueError, match="Invalid keyspace name"):
        db_manager.get_materialized_views("invalid;keyspace")
