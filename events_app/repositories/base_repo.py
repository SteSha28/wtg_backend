from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, TypeVar

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from events_app.db.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, data: dict):
        """Создать запись в базе с данными из словаря."""
        raise NotImplementedError

    @abstractmethod
    async def find_all(self,  offset: int, limit: int):
        """Получить список записей с пагинацией."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int):
        """Получить запись по ID."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, obj, fields: dict):
        """Обновить переданный объект новыми значениями."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int):
        """Удалить запись по ID."""
        raise NotImplementedError


class Repository(AbstractRepository, Generic[ModelType]):
    """
    Реализация абстрактного репозитория для модели SQLAlchemy
    с базовыми CRUD-операциями.
    """
    model: Optional[Type[ModelType]] = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict):
        stmt = (insert(self.model)
                .values(**data)
                .returning(self.model))
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def find_all(self, offset: int, limit: int):
        result = await self.session.execute(
            select(self.model).offset(offset).limit(limit))
        return result.scalars().all()

    async def get(self, id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def update(self, obj, fields: dict):
        for key, value in fields.items():
            setattr(obj, key, value)
        await self.session.flush()
        return obj

    async def delete(self, id: int):
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
