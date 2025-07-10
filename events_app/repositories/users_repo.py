from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base_repo import Repository
from events_app.db.models import (
    Event,
    SourceUser,
    User,
)


class UserRepository(Repository[User]):
    """Репозиторий для работы с пользователями."""
    model = User

    def __init__(self, session):
        super().__init__(session)

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Получить пользователя по ID.
        """
        result = await self.session.execute(
            select(self.model).filter_by(id=user_id)
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        """
        Получить пользователя по email.
        """
        result = await self.session.execute(
            select(self.model).filter_by(email=email)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        """
        Получить пользователя по username.
        """
        result = await self.session.execute(
            select(self.model).filter_by(username=username)
        )
        return result.scalars().first()

    async def update_avatar(self, user: User, avatar_path: str) -> User:
        """
        Обновить аватар пользователя.

        Args:
            - user (User): Пользователь.
            - avatar_path (str): Новый путь к изображению.

        Returns:
            - User: Обновлённый пользователь.
        """
        user.profile_image = avatar_path
        await self.session.flush()
        return user

    async def update_password(self, user: User, password: str) -> User:
        """
        Обновить хеш пароля пользователя.

        Args:
            - user (User): Пользователь.
            - password (str): Новый хеш пароля.

        Returns:
            - User: Обновлённый пользователь.
        """
        user.hashed_password = password
        await self.session.flush()
        return user

    async def add_favorite(self, user_id: int, event_id: int):
        """
        Добавить событие в избранное пользователя.

        Args:
            - user_id (int): ID пользователя.
            - event_id (int): ID события.
        """
        user = await self.session.get(User, user_id)
        event = await self.session.get(Event, event_id)
        if user and event and event not in user.favorites:
            user.favorites.append(event)

    async def remove_favorite(self, user_id: int, event_id: int):
        """
        Удалить событие из избранного пользователя.

        Args:
            - user_id (int): ID пользователя.
            - event_id (int): ID события.
        """
        user = await self.session.get(User, user_id)
        event = await self.session.get(Event, event_id)
        if user and event and event in user.favorites:
            user.favorites.remove(event)

    async def get_with_favorites(self, user_id: int):
        """
        Получить пользователя с избранными событиями
        (для событий подгружаются локации).

        Args:
            - user_id (int): ID пользователя.

        Returns:
            - User | None: Пользователь с загруженными избранными событиями.
        """
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.favorites)
                .selectinload(Event.location)
            )
            .where(User.id == user_id)
        )
        user = result.scalars().first()
        if user:
            for event in user.favorites:
                await self.session.refresh(event)
        return user


class SourceUserRepository(Repository[SourceUser]):
    """Репозиторий для работы с источниками пользователей."""
    model = SourceUser
