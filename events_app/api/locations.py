from fastapi import APIRouter, Depends, Query, status
from fastapi_cache.decorator import cache

from .dependencies import get_locations_service, get_admin_user
from events_app import schemas
from events_app.core.config import settings
from events_app.core.constants import LIMIT
from events_app.core.utils import custom_key_builder
from events_app.services.events_service import LocationService


locations_router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


@locations_router.get(
        "/",
        response_model=list[schemas.LocationFromDB],
)
async def get_locations(
    location_service: LocationService = Depends(get_locations_service),
):
    return await location_service.get_all()


@locations_router.get(
        "/{location_id}",
        response_model=schemas.LocationFromDB,
)
async def get_location(
    location_id: int,
    location_service: LocationService = Depends(get_locations_service),
):
    return await location_service.get(location_id)


@locations_router.get(
    "/{location_id}/events",
    response_model=schemas.PaginatedResponse,
)
@cache(expire=settings.REDIS_CACHE_EXPIRE, key_builder=custom_key_builder)
async def get_events_by_location(
    location_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(LIMIT, ge=1, le=1000),
    location_service: LocationService = Depends(get_locations_service),
):
    """
    Получить события по ID локации с пагинацией.
    Args:
        location_id (int): ID локации.
        offset (int, optional): Смещение для пагинации. По умолчанию 0.
        limit (int, optional): Лимит количества элементов. По умолчанию LIMIT.
        location_service (LocationService): Сервис локаций.

    Returns:
        PaginatedResponse: Объект с общим количеством,
        смещением, лимитом и списком событий.

    Кеширование результата с использованием Redis.
    """
    return await location_service.get_events_by_location(
        location_id, offset, limit)


@locations_router.post(
        "/",
        response_model=schemas.LocationFromDB,
)
async def add_location(
    location: schemas.LocationCreate,
    admin_user=Depends(get_admin_user),
    location_service: LocationService = Depends(get_locations_service),
):
    """
    Создаёт новую локацию.
    Требуется аутентификация администратора.
    """
    return await location_service.create(location)


@locations_router.put(
    '/{location_id}',
    response_model=schemas.LocationFromDB,
)
async def update_location(
    location_id: int,
    location: schemas.LocationCreate,
    admin_user=Depends(get_admin_user),
    location_service: LocationService = Depends(get_locations_service),
):
    """
    Обновляет данные локации по ID.
    Требуется аутентификация администратора.
    """
    return await location_service.update(location_id, location)


@locations_router.delete(
    '/{location_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_location(
    location_id: int,
    admin_user=Depends(get_admin_user),
    location_service: LocationService = Depends(get_locations_service),
):
    """
    Удаляет локацию по ID.
    Требуется аутентификация администратора.
    """
    return await location_service.delete(location_id)
