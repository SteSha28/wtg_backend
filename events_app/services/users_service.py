from typing import Callable, Generic, TypeVar

from events_app import schemas
from events_app.core.imageworker import remove_file_if_exists
from events_app.core.security import (
    hash_password,
    verify_password,
)
from events_app.services.base_service import BaseService
from events_app.uow.unit_of_work import IUnitOfWork

CreateUserSchema = TypeVar("CreateUserSchema", bound=schemas.BaseModel)
ReadUserSchema = TypeVar("ReadUserSchema", bound=schemas.BaseModel)


class UserService(BaseService[CreateUserSchema, ReadUserSchema],
                  Generic[CreateUserSchema, ReadUserSchema]):
    """
    Сервис для работы с пользователями:
    - получение по id, email, username
    - создание и аутентификация
    - обновление аватара
    - смена пароля
    - получение пользователя с избранным
    """
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]):
        super().__init__(uow_factory, "user", schemas.UserBase)

    async def get_by_id(
            self,
            user_id: int,
            ) -> schemas.UserFromDB | None:
        """Получить пользователя по ID."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_by_id(user_id)
            if user:
                return schemas.UserFromDB.model_validate(user)
            return None

    async def get_by_email(
            self,
            email: str,
            ) -> schemas.UserBase | None:
        """Получить пользователя по email."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_by_email(email)
            if user:
                return self.read_model.model_validate(user)
            return None

    async def get_by_username(
            self,
            username: str,
            ) -> schemas.UserBase | None:
        """Получить пользователя по имени пользователя."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_by_username(username)
            if user:
                return self.read_model.model_validate(user)
            return None

    async def check_user_exists(
            self,
            username: str,
            email: str,
            ) -> str | None:
        """Проверить, существует ли пользователь с таким email или username."""
        async with self.uow_factory() as uow:
            if await uow.user.get_by_email(email):
                return "Email already exists."
            if await uow.user.get_by_username(username):
                return "Username already exists."
            return None

    async def create_user(
            self,
            user: schemas.UserCreate,
            ) -> schemas.UserBase | str:
        """Создать нового пользователя с хэшированием пароля."""
        hashed_pwd = hash_password(user.password)
        user_data = user.model_dump()
        user_data['hashed_password'] = hashed_pwd
        del user_data['password']
        async with self.uow_factory() as uow:
            exist = await self.check_user_exists(
                user.username,
                user.email,
            )
            if exist:
                return exist
            return await uow.user.create(user_data)

    async def authenticate_user(
            self,
            email: str,
            password: str,
            ) -> int | None:
        """Проверить email и пароль, вернуть ID пользователя если
        успешна аутентификация."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_by_email(email)
            if user and verify_password(password, user.hashed_password):
                return user.id
            return None

    async def update_user_avatar(
            self,
            user_id: int,
            avatar_path: str,
            ) -> schemas.UserBase | None:
        """Обновить аватар пользователя, удалить старый файл, если он есть."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_by_id(user_id)
            if user:
                old_avatar = user.profile_image
                if old_avatar and old_avatar != avatar_path:
                    remove_file_if_exists(old_avatar)
                update_user = await uow.user.update_avatar(
                    user,
                    avatar_path,
                )
                return self.read_model.model_validate(update_user)
            return None

    async def change_password(
            self,
            user_id: int,
            last_pasword: str,
            new_password: str,
            ) -> schemas.UserBase | None:
        """Изменить пароль, проверив текущий."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_by_id(user_id)
            if not user or not verify_password(
                last_pasword,
                user.hashed_password
            ):
                raise ValueError("Incorrect data")
            hashed_password = hash_password(new_password)
            return await self.update_password(user_id, hashed_password)

    async def get_with_favorites(
            self,
            user_id: int
    ) -> schemas.UserWithFavorites | None:
        """Получить пользователя вместе с его избранным."""
        async with self.uow_factory() as uow:
            user = await uow.user.get_with_favorites(user_id)
            if user:
                return schemas.UserWithFavorites.model_validate(user)
            return None


class SourceUserService(
    BaseService[schemas.SourceUserCreate, schemas.SourceUserFromDB]
):
    """
    Сервис для работы с источниками пользователей.
    """
    def __init__(self, uow_factory: Callable[[], IUnitOfWork]):
        super().__init__(uow_factory, "source_user", schemas.SourceUserFromDB)
