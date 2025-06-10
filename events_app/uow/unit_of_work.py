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
    source_user: AbstractRepository
    user: AbstractRepository
    events: AbstractRepository
    location: AbstractRepository
    category: AbstractRepository
    tag: AbstractRepository

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, traceback):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self._session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self._session_factory()
        self.source_user = SourceUserRepository(self.session)
        self.user = UserRepository(self.session)
        self.events = EventRepository(self.session)
        self.location = LocationRepository(self.session)
        self.category = CategoryRepository(self.session)
        self.tag = TagRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, traceback):
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            if hasattr(self, "session"):
                await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
