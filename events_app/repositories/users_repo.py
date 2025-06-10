from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base_repo import Repository
from events_app.db.models import (
    Event,
    SourceUser,
    User,
)


class UserRepository(Repository[User]):
    model = User

    def __init__(self, session):
        super().__init__(session)

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(self.model).filter_by(id=user_id)
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(self.model).filter_by(email=email)
        )
        return result.scalars().first()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(self.model).filter_by(username=username)
        )
        return result.scalars().first()

    async def update_avatar(self, user: User, avatar_path: str) -> User:
        user.profile_image = avatar_path
        await self.session.flush()
        return user

    async def update_password(self, user: User, password: str) -> User:
        user.hashed_password = password
        await self.session.flush()
        return user

    async def add_favorite(self, user_id: int, event_id: int):
        user = await self.session.get(User, user_id)
        event = await self.session.get(Event, event_id)
        if user and event and event not in user.favorites:
            user.favorites.append(event)

    async def remove_favorite(self, user_id: int, event_id: int):
        user = await self.session.get(User, user_id)
        event = await self.session.get(Event, event_id)
        if user and event and event in user.favorites:
            user.favorites.remove(event)

    async def get_with_favorites(self, user_id: int):
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
    model = SourceUser
