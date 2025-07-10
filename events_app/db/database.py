from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from events_app.core.config import settings


engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    """Базовый класс для декларативных моделей SQLAlchemy."""
    pass


async def get_async_session():
    """Получение асинхронной сессии БД."""
    async with async_session_maker() as session:
        yield session
