from typing import Callable, Generic, TypeVar

from events_app.core.constants import LIMIT
from events_app.schemas.users import BaseModel
from events_app.repositories.base_repo import Repository
from events_app.uow.unit_of_work import IUnitOfWork

CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
ReadSchema = TypeVar("ReadSchema", bound=BaseModel)


class BaseService(Generic[CreateSchema, ReadSchema]):
    """
    Базовый сервис для работы с сущностями через Unit of Work и репозитории.

    Args:
        - uow_factory (Callable[[], IUnitOfWork]): Фабрика для
            создания UnitOfWork.
        - repo_attr (str): Имя атрибута репозитория в UnitOfWork.
        - read_model (type[ReadSchema]): Pydantic-модель для валидации
            возвращаемых данных.
    """
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        repo_attr: str,
        read_model: type[ReadSchema],
    ):
        self.uow_factory = uow_factory
        self.repo_attr = repo_attr
        self.read_model = read_model

    async def _get_repo(
            self,
            uow: IUnitOfWork,
    ) -> Repository:
        """
        Получить репозиторий из UnitOfWork по имени атрибута.

        Args:
            - uow (IUnitOfWork): Экземпляр UnitOfWork.

        Returns:
            - Repository: Репозиторий для работы с данными.
        """
        return getattr(uow, self.repo_attr)

    async def create(
            self,
            create_schema: CreateSchema,
    ):
        """
        Создать объект в базе данных.

        Args:
            - create_schema (CreateSchema): Pydantic-схема с данными
              для создания нового объекта.

        Returns:
            - ReadSchema: Созданный объект, валидированный Pydantic-моделью.
        """
        async with self.uow_factory() as uow:
            repo = await self._get_repo(uow)
            db_obj = await repo.create(create_schema.model_dump())
            return self.read_model.model_validate(db_obj)

    async def get(
            self,
            obj_id: int,
    ) -> ReadSchema | None:
        """
        Получить объект по ID.

        Args:
            - obj_id (int): Идентификатор объекта.

        Returns:
            - ReadSchema | None: Найденный объект или None.
        """
        async with self.uow_factory() as uow:
            repo = await self._get_repo(uow)
            db_obj = await repo.get(obj_id)
            if db_obj:
                return self.read_model.model_validate(db_obj)
            return None

    async def get_all(
            self,
            limit: int = LIMIT,
            offset: int = 0,
    ) -> list[ReadSchema]:
        """
        Получить список объектов с пагинацией.

        Args:
            - limit (int, optional): Лимит на количество объектов.
                По умолчанию LIMIT.
            - offset (int, optional): Смещение. По умолчанию 0.

        Returns:
            - list[ReadSchema]: Список валидированных объектов.
        """
        async with self.uow_factory() as uow:
            repo = getattr(uow, self.repo_attr)
            objects = await repo.find_all(offset, limit)
            return [self.read_model.model_validate(obj) for obj in objects]

    async def update(
            self,
            obj_id: int,
            update_schema: CreateSchema,
    ):
        """
        Обновить объект по ID.

        Args:
            - obj_id (int): Идентификатор обновляемого объекта.
            - update_schema (CreateSchema): Данные для обновления.

        Returns:
            - ReadSchema | None: Обновлённый объект или None, если не найден.
        """
        async with self.uow_factory() as uow:
            repo = await self._get_repo(uow)
            db_obj = await repo.get(obj_id)
            if db_obj:
                updated_obj = await repo.update(
                    db_obj,
                    update_schema.model_dump(exclude_unset=True),
                )
                return self.read_model.model_validate(updated_obj)
            return None

    async def delete(
            self,
            obj_id: int,
    ) -> bool:
        """
        Удалить объект по ID.

        Args:
            - obj_id (int): Идентификатор удаляемого объекта.

        Returns:
            - bool: True если удалено, иначе False.
        """
        async with self.uow_factory() as uow:
            repo = await self._get_repo(uow)
            db_obj = await repo.get(obj_id)
            if db_obj:
                await repo.delete(db_obj.id)
                await uow.commit()
                return True
            return False
