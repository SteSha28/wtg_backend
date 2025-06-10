from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from events_app.core.auth import create_jwt_token
from events_app.db.redis_db import store_token
from events_app.services.users_service import UserService
from events_app.schemas import TokenResponce


class AuthService:
    def __init__(
            self,
            user_service: UserService,
            redis: Redis,
    ):
        self.user_service = user_service
        self.redis = redis

    async def login(
            self,
            form_data: OAuth2PasswordRequestForm
    ) -> TokenResponce:
        user = await self.user_service.authenticate_user(
            form_data.username,
            form_data.password,
        )
        if not user:
            raise ValueError("User not found or wrong credentials")

        token = create_jwt_token(data={"id": user})
        await store_token(self.redis, token, user_id=user)
        return TokenResponce(Authorization=token, id=user)
