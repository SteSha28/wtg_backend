from fastapi import APIRouter, Depends, status

from .dependencies import get_tags_service, get_admin_user
from events_app import schemas
from events_app.services.events_service import TagService


tags_router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


@tags_router.get(
        "/",
        response_model=list[schemas.TagFromDB]
)
async def get_tags(
    tags_service: TagService = Depends(get_tags_service),
):
    return await tags_service.get_all()


@tags_router.get(
        "/{tag_id}",
        response_model=schemas.TagFromDB
)
async def get_tag(
    tag_id: int,
    tags_service: TagService = Depends(get_tags_service),
):
    return await tags_service.get(tag_id)


@tags_router.post(
        "/",
        response_model=schemas.TagFromDB
)
async def add_tag(
    tag: schemas.TagCreate,
    admin_user=Depends(get_admin_user),
    tags_service: TagService = Depends(get_tags_service),
):
    """
    Создаёт новый тег.
    Требуется аутентификация администратора.
    """
    return await tags_service.create(tag)


@tags_router.put(
    '/{tag_id}',
    response_model=schemas.TagFromDB
)
async def update_tag(
    tag_id: int,
    tag: schemas.TagCreate,
    admin_user=Depends(get_admin_user),
    tags_service: TagService = Depends(get_tags_service),
):
    """
    Обновляет данные тега по ID.
    Требуется аутентификация администратора.
    """
    return await tags_service.update(
        tag_id,
        tag,
    )


@tags_router.delete(
    '/{tag_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tag(
    tag_id: int,
    admin_user=Depends(get_admin_user),
    tags_service: TagService = Depends(get_tags_service),
):
    """
    Удаляет тег по ID.
    Требуется аутентификация администратора.
    """
    await tags_service.delete(tag_id)
