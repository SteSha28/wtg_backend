from datetime import date
from typing import Optional

from fastapi import (
    APIRouter, Depends, File,
    Query, status, UploadFile,
)
from fastapi_cache.decorator import cache

from .dependencies import get_events_service, get_admin_user
from events_app import schemas
from events_app.core.config import settings
from events_app.core.constants import LIMIT
from events_app.core.imageworker import upload_image, EVENTS_IMAGE_DIR
from events_app.core.utils import custom_key_builder
from events_app.services.events_service import EventService


events_router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@events_router.get(
        "/",
        response_model=schemas.PaginatedResponse
)
@cache(expire=settings.REDIS_CACHE_EXPIRE, key_builder=custom_key_builder)
async def get_events(
    date: Optional[date] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    time: Optional[int] = Query(None, ge=0, le=23),
    offset: int = Query(0, ge=0),
    limit: int = Query(LIMIT, ge=1, le=1000),
    events_service: EventService = Depends(get_events_service),
):
    """
    Получить список мероприятий с поддержкой пагинации и
    фильтрации по дате и времени.

    Фильтрация:
    - date: конкретная дата мероприятия
    - date_from / date_to: диапазон дат (включительно)
    - time: час начала (от 0 до 23)

    Параметры пагинации:
    - offset: смещение от начала списка. По умолчанию 0.
    - limit: количество мероприятий (макс. 1000). По умолчанию
        задано переменной LIMIT.
    """
    if date or date_from or date_to or time:
        return await events_service.get_filtered(
            date, date_from, date_to, time, offset, limit)
    else:
        return await events_service.get_all(offset, limit)


@events_router.get(
        "/search",
        response_model=list[schemas.SearchResult],
)
async def autocomplete(
    query: str = Query(..., min_length=1),
    events_service: EventService = Depends(get_events_service),
):
    """
    Автодополнение по названию мероприятия или названию локации.
    """
    return await events_service.search_autocomplete(query)


@events_router.get(
        "/{event_id}",
        response_model=schemas.EventFromDB
)
async def get_event(
    event_id: int,
    events_service: EventService = Depends(get_events_service),
):
    return await events_service.get(event_id)


@events_router.post(
        "/",
        response_model=schemas.EventFromDB
)
async def add_events(
    event: schemas.EventCreate,
    admin_user=Depends(get_admin_user),
    events_service: EventService = Depends(get_events_service),
):
    """
    Создаёт новое мероприятие.
    Требуется аутентификация администратора.
    """
    return await events_service.create(event)


@events_router.put(
    '/{event_id}',
    response_model=schemas.EventFromDB
)
async def update_event(
    event_id: int,
    event: schemas.EventCreate,
    admin_user=Depends(get_admin_user),
    events_service: EventService = Depends(get_events_service),
):
    """
    Обновляет данные о мероприятии по ID.
    Требуется аутентификация администратора.
    """
    return await events_service.update(
        event_id,
        event,
    )


@events_router.delete(
    '/{event_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_event(
    event_id: int,
    admin_user=Depends(get_admin_user),
    events_service: EventService = Depends(get_events_service),
):
    """
    Удаляет мероприятие по ID.
    Требуется аутентификация администратора.
    """
    await events_service.delete(event_id)


@events_router.put(
    '/{event_id}/event-image',
    response_model=schemas.EventFromDB
)
async def upload_event_image(
    event_id: int,
    file: UploadFile = File(...),
    admin_user=Depends(get_admin_user),
    events_service: EventService = Depends(get_events_service),
):
    """
    Добавляет изображение мероприятия по ID.
    Требуется аутентификация администратора.
    """
    event_image = await upload_image(file, EVENTS_IMAGE_DIR)
    return await events_service.update_event_image(
        event_id,
        event_image['image']
    )


@events_router.delete(
    '/{event_id}/event-image',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_event_image(
    event_id: int,
    admin_user=Depends(get_admin_user),
    events_service: EventService = Depends(get_events_service),
):
    """
    Удаляет изображение мероприятия по ID.
    Требуется аутентификация администратора.
    """
    return await events_service.update_event_image(event_id, '')
