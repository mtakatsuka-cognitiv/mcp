import pytest
from postgresql_mcp.db import DatabaseManager


@pytest.fixture
def db_manager():
    return DatabaseManager({})


def test_validate_name_valid():
    """Test that valid names pass validation"""
    valid_names = [
        "public",
        "my_schema",
        "schema123",
        "UPPERCASE",
        "_hidden",
        "users",
        "user_profiles",
        "table123",
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
    ]

    for name in invalid_names:
        with pytest.raises(ValueError, match="Invalid name"):
            DatabaseManager.validate_name(name)


def test_get_table_indexes_validation(db_manager):
    """Test that get_table_indexes validates schema and table names"""
    with pytest.raises(ValueError, match="Invalid schema name"):
        db_manager.get_table_indexes("invalid;schema", "valid_table")

    with pytest.raises(ValueError, match="Invalid table name"):
        db_manager.get_table_indexes("public", "invalid;table")


def test_get_table_constraints_validation(db_manager):
    """Test that get_table_constraints validates schema and table names"""
    with pytest.raises(ValueError, match="Invalid schema name"):
        db_manager.get_table_constraints("invalid;schema", "valid_table")

    with pytest.raises(ValueError, match="Invalid table name"):
        db_manager.get_table_constraints("public", "invalid;table")
