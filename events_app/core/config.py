import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_JWT_HOST: str
    REDIS_JWT_PORT: str
    REDIS_CACHE_HOST: str
    REDIS_CACHE_PORT: str
    REDIS_CACHE_EXPIRE: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE: int

    @property
    def ASYNC_DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        if not os.path.exists(env_file):
            print(f"Файл .env не найден по пути: {env_file}")


settings = Settings()
