from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator
from .config import settings

# Create async engine using the constructed database URL with async driver
engine = create_async_engine(settings.get_database_url(async_driver=True), echo=True)

# Create async session maker
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Create declarative base
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()