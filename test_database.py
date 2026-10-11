from sqlalchemy import create_engine, inspect

from init_db import create_database_tables


def test_create_database_tables_adds_missing_relationship_tables():
    test_engine = create_engine("sqlite://")
    try:
        create_database_tables(test_engine)
        table_names = set(inspect(test_engine).get_table_names())

        assert {"team_week", "week"}.issubset(table_names)
    finally:
        test_engine.dispose()
