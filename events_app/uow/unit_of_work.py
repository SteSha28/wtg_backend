from abc import ABC, abstractmethod

from events_app.db.database import async_session_maker
from events_app.repositories.users_repo import (
    SourceUserRepository,
    UserRepository,
)
from events_app.repositories.base_repo import AbstractRepository
from events_app.repositories.events_repo import (
    EventRepository,
    LocationRepository,
    CategoryRepository,
    TagRepository,
)


class IUnitOfWork(ABC):
    """
    Абстрактный интерфейс Unit of Work для управления
    транзакциями и репозиториями.
    """
    source_user: AbstractRepository
    user: AbstractRepository
    events: AbstractRepository
    location: AbstractRepository
    category: AbstractRepository
    tag: AbstractRepository

    @abstractmethod
    def __init__(self):
        """Инициализация Unit of Work."""
        ...

    @abstractmethod
    async def __aenter__(self):
        """Вход в асинхронный контекстный менеджер."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, traceback):
        """
        Выход из асинхронного контекстного менеджера.
        Выполняет commit или rollback в зависимости от наличия исключения.
        """
        ...

    @abstractmethod
    async def commit(self):
        """Фиксация изменений в базе данных."""
        ...

    @abstractmethod
    async def rollback(self):
        """Откат изменений в базе данных."""
        ...


class UnitOfWork(IUnitOfWork):
    """
    Конкретная реализация Unit of Work
    с использованием SQLAlchemy AsyncSession.
    """
    def __init__(self):
        """Создаёт фабрику сессий."""
        self._session_factory = async_session_maker

    async def __aenter__(self):
        """Создаёт сессию и инициализирует репозитории."""
        self.session = self._session_factory()
        self.source_user = SourceUserRepository(self.session)
        self.user = UserRepository(self.session)
        self.events = EventRepository(self.session)
        self.location = LocationRepository(self.session)
        self.category = CategoryRepository(self.session)
        self.tag = TagRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        """Закрывает сессию, выполняет commit или rollback."""
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if hasattr(self, "session"):
                await self.session.close()

    async def commit(self):
        """Фиксирует изменения."""
        await self.session.commit()

    async def rollback(self):
        """Откатывает изменения."""
        await self.session.rollback()
