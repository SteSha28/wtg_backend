from typing import Callable, Generic, TypeVar

from events_app.core.constants import LIMIT
from events_app.schemas.users import BaseModel
from events_app.repositories.base_repo import Repository
from events_app.uow.unit_of_work import IUnitOfWork

CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
ReadSchema = TypeVar("ReadSchema", bound=BaseModel)


class BaseService(Generic[CreateSchema, ReadSchema]):
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
        return getattr(uow, self.repo_attr)

    async def create(
            self,
            create_schema: CreateSchema,
    ):
        async with self.uow_factory() as uow:
            repo = await self._get_repo(uow)
            db_obj = await repo.create(create_schema.model_dump())
            return self.read_model.model_validate(db_obj)

    async def get(
            self,
            obj_id: int,
    ) -> ReadSchema | None:
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
        async with self.uow_factory() as uow:
            repo = getattr(uow, self.repo_attr)
            objects = await repo.find_all(offset, limit)
            return [self.read_model.model_validate(obj) for obj in objects]

    async def update(
            self,
            obj_id: int,
            update_schema: CreateSchema,
    ):
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
    ):
        async with self.uow_factory() as uow:
            repo = await self._get_repo(uow)
            db_obj = await repo.get(obj_id)
            if db_obj:
                await repo.delete(db_obj.id)
                await uow.commit()
                return True
            return False
