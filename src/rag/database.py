"""
Database Setup & Management

Initialize PostgreSQL + setup Alembic for migrations.
"""

import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager

from src.rag.models import Base

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "scientific_agent",
        user: str = "postgres",
        password: str = "postgres",
        echo: bool = False,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.echo = echo

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "scientific_agent"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
        )

    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )

    def __repr__(self):
        return f"<DatabaseConfig {self.user}@{self.host}:{self.port}/{self.database}>"


class Database:
    """Database connection manager."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None

    def init(self):
        """Initialize database connection and create tables."""
        logger.info(f"Initializing database: {self.config}")

        # Create engine
        self.engine = create_engine(
            self.config.connection_string,
            echo=self.config.echo,
            poolclass=NullPool,  # No connection pooling (for simplicity)
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

        # Test connection
        try:
            with self.engine.connect() as conn:
                logger.info("✓ Database connection successful")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise

    def create_tables(self):
        """Create all tables from models."""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("✓ Tables created")

    def drop_tables(self):
        """Drop all tables (WARNING: destructive)."""
        logger.warning("⚠️  Dropping all tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("✓ Tables dropped")

    @contextmanager
    def get_session(self) -> Session:
        """Get database session (context manager)."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("✓ Database connection closed")


# Global database instance
_db_instance: Optional[Database] = None


def init_database(config: Optional[DatabaseConfig] = None) -> Database:
    """Initialize and return global database instance."""
    global _db_instance

    if config is None:
        config = DatabaseConfig.from_env()

    _db_instance = Database(config)
    _db_instance.init()
    _db_instance.create_tables()

    return _db_instance


def get_database() -> Database:
    """Get global database instance."""
    global _db_instance

    if _db_instance is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() first."
        )

    return _db_instance


def get_session() -> Session:
    """Get database session."""
    db = get_database()
    return db.SessionLocal()
