from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from sqlalchemy import create_engine,event
from app.core.config import settings
from sqlalchemy.orm import sessionmaker,declarative_base
from contextlib import asynccontextmanager


Base = declarative_base()

engine = create_engine(
    settings.DB_URI,
    pool_pre_ping=True,
    pool_size=5,            # Keep sync pool small; main traffic is async
)

# --- ASYNC CONFIG (For high-concurrency API calls) ---
async_engine = create_async_engine(
    settings.ASYNC_DB_URI,
    pool_size=20,           # Baseline connections always ready
    max_overflow=50,        # Higher overflow for your 1,000 user goal
    pool_timeout=60,        # Wait longer before failing during a huge spike
    pool_recycle=1800,
    pool_pre_ping=True,      # Crucial: checks if connection is alive before using it
)


# 2. Create a Session Factory
async_session_pool = async_sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False         # Better performance: manually flush when needed
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

async def get_async_db():
    """Provides a transactional scope around a series of operations."""
    async with async_session_pool() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db():
    """Sync session with soft-delete filtering for FastAPI dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        


