from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    status,
    UploadFile,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)

from events_app import schemas
from events_app.api.dependencies import (
    AuthService,
    FavoriteService,
    UserService,
    get_auth_service,
    get_current_user,
    get_favorite_service,
    get_redis_connection,
    get_users_service,
    check_user_access,
    find_user,
)
from events_app.core.exceptions import (
    BadRequestException,
)
from events_app.core.imageworker import upload_image, AVATAR_DIR
from events_app.db.redis_db import delete_token
from redis.asyncio import Redis


users_router = APIRouter(
    prefix='/users',
    tags=["Users"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


@users_router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: schemas.UserCreate,
    user_service: UserService = Depends(get_users_service),
):
    """
    Регистрирует нового пользователя.

    Returns:
        None или BadRequestException, если пользователь уже существует.
    """
    result = await user_service.create_user(user)
    if isinstance(result, str):
        return BadRequestException(result)


@users_router.post(
    '/login',
    response_model=schemas.TokenResponce,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Аутентифицирует пользователя и возвращает access токен.
    """
    return await auth_service.login(form_data)


@users_router.delete(
    '/logout',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    redis: Redis = Depends(get_redis_connection),
):
    """
    Удаляет токен из Redis и завершает сессию пользователя.
    """
    await delete_token(redis, token)


@users_router.get(
    '/{user_id}',
    response_model=schemas.UserWithFavorites,
)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_users_service),
):
    user = await find_user(user_id, user_service)
    return await user_service.get_with_favorites(user.id)


@users_router.put(
    '/{user_id}',
    response_model=schemas.UserUpdate,
)
async def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    user_token_id: int = Depends(check_user_access),
    user_service: UserService = Depends(get_users_service),
):
    """
    Обновляет профиль пользователя. Доступен только владельцу.
    """
    user = await user_service.update(
        user_token_id,
        user_data,
    )
    return user


@users_router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    user_token_id: int = Depends(check_user_access),
    user_service: UserService = Depends(get_users_service),
):
    """
    Удаляет пользователя. Доступен только владельцу.
    """
    await user_service.delete(user_token_id)


@users_router.put(
    '/{user_id}/avatar',
    response_model=schemas.AvatarResponce,
)
async def upload_user_avatar(
    user_id: int,
    file: UploadFile = File(...),
    user_token_id: int = Depends(check_user_access),
    user_service: UserService = Depends(get_users_service),
):
    """
    Загружает аватар пользователя. Доступен только владельцу.
    """
    profile_image = await upload_image(file, AVATAR_DIR)
    return await user_service.update_user_avatar(
        user_token_id, profile_image['image'])


@users_router.delete(
    '/{user_id}/avatar',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_avatar(
    user_id: int,
    user_token_id: int = Depends(check_user_access),
    user_service: UserService = Depends(get_users_service),
):
    """
    Удаляет аватар пользователя. Доступен только владельцу.
    """
    return await user_service.update_user_avatar(user_token_id, '')


@users_router.put(
        '/{user_id}/change-password',
        response_model=schemas.UserUpdate,
)
async def change_password(
    user_id: int,
    user_data: schemas.PasswordChange,
    user_token_id: int = Depends(get_current_user),
    user_service: UserService = Depends(get_users_service),
):
    """
    Изменяет пароль пользователя. Требуется текущий и новый пароли.

    Raises:
        - BadRequestException: если текущий пароль неверный.
    """
    try:
        user = await user_service.change_password(
            user_token_id,
            user_data.last_password,
            user_data.password,
            )
        return user
    except ValueError as e:
        return BadRequestException(detail={e})


@users_router.post(
    "/favorites/{event_id}",
)
async def add_to_favorites(
    event_id: int,
    user_token_id: int = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    await favorite_service.add_favorite(user_token_id, event_id)


@users_router.delete(
        "/favorites/{event_id}",
)
async def remove_from_favorites(
    event_id: int,
    user_token_id: int = Depends(get_current_user),
    favorite_service: FavoriteService = Depends(get_favorite_service),
):
    await favorite_service.remove_favorite(user_token_id, event_id)
