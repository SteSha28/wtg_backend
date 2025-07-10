from fastapi import APIRouter, Depends, Query, status
from fastapi_cache.decorator import cache

from .dependencies import get_categories_service, get_admin_user
from events_app import schemas
from events_app.core.config import settings
from events_app.core.constants import LIMIT
from events_app.core.utils import custom_key_builder
from events_app.services.events_service import CategoryService


categories_router = APIRouter(
    prefix="/category",
    tags=["Category"]
)


@categories_router.get(
        "/",
        response_model=list[schemas.CategoryFromDB],
)
async def get_categories(
    category_service: CategoryService = Depends(get_categories_service),
):
    return await category_service.get_all()


@categories_router.get(
    "/{category_id}",
    response_model=schemas.CategoryFromDB,
)
async def get_category(
    category_id: int,
    category_service: CategoryService = Depends(get_categories_service),
):
    return await category_service.get(category_id)


@categories_router.get(
    "/{category_id}/events",
    response_model=schemas.PaginatedResponse,
)
@cache(expire=settings.REDIS_CACHE_EXPIRE, key_builder=custom_key_builder)
async def get_events_by_category(
    category_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(LIMIT, ge=1, le=1000),
    category_service: CategoryService = Depends(get_categories_service),
):
    """
    Возвращает список событий для категории с пагинацией.

    Args:
        - category_id (int): ID категории.
        - offset (int, optional): Смещение для пагинации. По умолчанию 0.
        - limit (int, optional): Лимит количества элементов. По умолчанию
            задано переменной LIMIT.
        - category_service (CategoryService): Сервис категорий.

    Returns:
        - PaginatedResponse: Объект с общим количеством,
            смещением, лимитом и списком событий.
    """
    return await category_service.get_events_by_category(
        category_id, offset, limit)


@categories_router.post(
        "/",
        response_model=schemas.CategoryFromDB
)
async def add_category(
    category: schemas.CategoryCreate,
    admin_user=Depends(get_admin_user),
    category_service: CategoryService = Depends(get_categories_service),
):
    """
    Создаёт новую категорию.
    Требуется аутентификация администратора.
    """
    return await category_service.create(category)


@categories_router.put(
    "/{category_id}",
    response_model=schemas.CategoryFromDB,
)
async def update_category(
    category_id: int,
    category: schemas.CategoryCreate,
    admin_user=Depends(get_admin_user),
    category_service: CategoryService = Depends(get_categories_service),
):
    """
    Обновляет данные категории по ID.
    Требуется аутентификация администратора.
    """
    return await category_service.update(category_id, category)


@categories_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    admin_user=Depends(get_admin_user),
    category_service: CategoryService = Depends(get_categories_service),
):
    """
    Удаляет категорию по ID.
    Требуется аутентификация администратора.
    """
    return await category_service.delete(category_id)
