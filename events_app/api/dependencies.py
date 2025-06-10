from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis

from events_app.core import exceptions
from events_app.db.redis_db import (
    check_token,
    get_redis_connection,
)
from events_app.services.auth_service import AuthService
from events_app.services.events_service import (
    EventService, CategoryService, FavoriteService,
    LocationService, TagService,
)
from events_app.services.users_service import UserService
from events_app.uow.unit_of_work import UnitOfWork


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_users_service() -> UserService:
    return UserService(uow_factory=UnitOfWork)


async def get_tags_service() -> TagService:
    return TagService(uow_factory=UnitOfWork)


async def get_locations_service() -> LocationService:
    return LocationService(uow_factory=UnitOfWork)


async def get_events_service() -> EventService:
    return EventService(uow_factory=UnitOfWork)


async def get_categories_service() -> CategoryService:
    return CategoryService(uow_factory=UnitOfWork)


async def get_auth_service(
    user_service: UserService = Depends(get_users_service),
    redis: Redis = Depends(get_redis_connection),
) -> AuthService:
    return AuthService(user_service=user_service, redis=redis)


async def get_favorite_service() -> FavoriteService:
    return FavoriteService(uow_factory=UnitOfWork)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    redis: Redis = Depends(get_redis_connection),
) -> int:
    user_id = await check_token(redis, token)
    if user_id is None:
        raise exceptions.UnauthorizedException()
    return user_id


async def check_user_access(
    user_id: int,
    token_user_id: int = Depends(get_current_user)
) -> int:
    if user_id != token_user_id:
        raise exceptions.ForbiddenException()
    return user_id


async def find_user(
    user_id: int,
    user_service: UserService,
):
    user = await user_service.get_by_id(user_id)
    if not user:
        raise exceptions.NotFoundException()
    return user


async def get_admin_user(
    token: str = Depends(oauth2_scheme),
):
    redis = await get_redis_connection()
    user_id = await check_token(redis, token)
    if user_id is None:
        raise exceptions.UnauthorizedException()

    user_service = await get_users_service()
    user = await user_service.get_by_id(user_id)
    if user is None or not user.is_admin:
        raise exceptions.ForbiddenException()

    return user
