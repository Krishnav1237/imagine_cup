"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
from app.config import settings
from app.models.models import Base


# Create engine based on deployment mode
if settings.is_local:
    # SQLite engine with special configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL engine for Azure
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized in {settings.DEPLOYMENT_MODE} mode")
    print(f"📊 Database URL: {settings.DATABASE_URL}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """
    WARNING: Drops all tables and recreates them
    Use only in development/testing
    """
    if settings.is_local:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("🔄 Database reset completed")
    else:
        raise RuntimeError("Database reset not allowed in production mode")