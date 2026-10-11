"""Initialize missing SQLAlchemy tables before serving the API."""

import models  # noqa: F401 - register model tables with SQLAlchemy metadata
from sqlalchemy.engine import Engine

from database import Base, engine


def create_database_tables(database_engine: Engine = engine) -> None:
    """Create model tables that are missing from the configured database."""
    Base.metadata.create_all(bind=database_engine)


if __name__ == "__main__":
    create_database_tables()
