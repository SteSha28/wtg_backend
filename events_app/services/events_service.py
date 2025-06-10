from datetime import date
from typing import Callable, Generic, Optional, TypeVar

from events_app import schemas
from events_app.core.imageworker import remove_file_if_exists
from events_app.services.base_service import BaseService
from events_app.uow.unit_of_work import IUnitOfWork

CreateEventSchema = TypeVar("CreateEventSchema", bound=schemas.BaseModel)
ReadEventSchema = TypeVar("ReadEventSchema", bound=schemas.BaseModel)


class EventService(
    BaseService[CreateEventSchema, ReadEventSchema],
    Generic[CreateEventSchema, ReadEventSchema]
):
    def __init__(
        self,
        uow_factory: Callable[[], IUnitOfWork],
        read_model: type[ReadEventSchema] = schemas.EventFromDB,
    ):
        super().__init__(uow_factory, "events", read_model)

    async def get_all(
            self,
            offset: int,
            limit: int,
    ) -> schemas.PaginatedResponse[schemas.EventShort]:
        async with self.uow_factory() as uow:
            events = await uow.events.find_all(offset, limit)
            total = await uow.events.count_all()
            return schemas.PaginatedResponse[schemas.EventShort](
                total=total,
                offset=offset,
                limit=limit,
                items=[schemas.EventShort.model_validate(event)
                       for event in events]
            )

    async def create(
            self,
            create_schema: schemas.EventCreate
    ) -> schemas.EventFromDB:
        async with self.uow_factory() as uow:
            event = await uow.events.create(create_schema.model_dump())
            return self.read_model.model_validate(event)

    async def get(
            self,
            obj_id: int,
    ) -> schemas.EventFromDB | None:
        async with self.uow_factory() as uow:
            db_obj = await uow.events.get(obj_id)
            if db_obj:
                return schemas.EventFromDB.model_validate(db_obj)
            return None

    async def get_filtered(
        self,
        date: Optional[date],
        date_from: Optional[date],
        date_to: Optional[date],
        hour: Optional[int],
        offset: int,
        limit: int,
    ) -> schemas.PaginatedResponse[schemas.EventShort]:
        async with self.uow_factory() as uow:
            events = await uow.events.find_by_date_filter(
                date, date_from, date_to, hour, offset, limit)

            total = await uow.events.count_filtered(
                date, date_from, date_to, hour
            )

            return schemas.PaginatedResponse[schemas.EventShort](
                total=total,
                offset=offset,
                limit=limit,
                items=[schemas.EventShort.model_validate(event)
                       for event in events]
            )

    async def update_event_image(
            self,
            event_id: int,
            image_path: str,
    ) -> schemas.EventFromDB | None:
        async with self.uow_factory() as uow:
            event = await uow.events.get(event_id)
            if event:
                old_image = event.event_image
                if old_image and old_image != image_path:
                    remove_file_if_exists(old_image)
                update_event = await uow.events.update_image(
                    event,
                    image_path,
                )
                return self.read_model.model_validate(update_event)
            return None

    async def search_autocomplete(
            self,
            query: str
    ) -> list[schemas.SearchResult]:
        async with self.uow_factory() as uow:
            return await uow.events.search_titles_and_locations(query)


class LocationService(
    BaseService[schemas.LocationCreate, schemas.LocationFromDB]
):
    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
    ):
        super().__init__(uow_factory, "location", schemas.LocationFromDB)

    async def get_events_by_location(
            self,
            location_id: int,
            offset: int,
            limit: int,
    ) -> schemas.PaginatedResponse[schemas.EventShort]:
        async with self.uow_factory() as uow:
            events = await uow.events.find_by_location(
                location_id, offset, limit)
            total = await uow.events.count_by_location(location_id)
            return schemas.PaginatedResponse[schemas.EventShort](
                total=total,
                offset=offset,
                limit=limit,
                items=[schemas.EventShort.model_validate(event)
                       for event in events]
            )


class TagService(BaseService[schemas.TagCreate, schemas.TagFromDB]):
    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
    ):
        super().__init__(uow_factory, 'tag', schemas.TagFromDB)


class CategoryService(
    BaseService[schemas.CategoryCreate, schemas.CategoryFromDB]
):
    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
    ):
        super().__init__(uow_factory, "category", schemas.CategoryFromDB)

    async def get_events_by_category(
            self,
            category_id: int,
            offset: int,
            limit: int,
    ) -> schemas.PaginatedResponse[schemas.EventShort]:
        async with self.uow_factory() as uow:
            events = await uow.events.find_by_category(
                category_id, offset, limit)
            total = await uow.events.count_by_category(category_id)
            return schemas.PaginatedResponse[schemas.EventShort](
                total=total,
                offset=offset,
                limit=limit,
                items=[schemas.EventShort.model_validate(event)
                       for event in events]
            )


class FavoriteService:
    def __init__(
            self,
            uow_factory: Callable[[], IUnitOfWork],
    ):
        self.uow_factory = uow_factory

    async def add_favorite(self, user_id: int, event_id: int):
        async with self.uow_factory() as uow:
            await uow.user.add_favorite(user_id, event_id)

    async def remove_favorite(self, user_id: int, event_id: int):
        async with self.uow_factory() as uow:
            await uow.user.remove_favorite(user_id, event_id)

    async def get_user_favorites(
            self,
            user_id: int
    ) -> list[schemas.EventShort]:
        async with self.uow_factory() as uow:
            user = await uow.user.get_with_favorites(user_id)
            return user.favorites if user else []
