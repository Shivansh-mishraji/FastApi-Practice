# db.py: Database connection configurations and helpers using async SQLAlchemy
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine with DB logging enabled if configured
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create session maker session factory for async sessions
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Declarative Base for models
Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for injecting async database sessions into API routes.
    Automatically closes the session after the request finishes.
    """
    async with async_session_maker() as session:
        yield session

async def init_db():
    """
    Helper to initialize database and create tables.
    Runs on application startup within the lifespan context manager.
    """
    async with engine.begin() as conn:
        # Import models here to ensure they are registered on Base.metadata before creation
        import app.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
