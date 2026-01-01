"""Database configuration and connection setup using SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./fantasy_data.db" # SQLite database URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
) # create an engine object
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # create a session that points to the engine and adds a couple of more config settings

Base = declarative_base() # create a base class for our models to inherit from

