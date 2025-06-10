from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqladmin import Admin
import uvicorn

from events_app import api
from events_app.api.dependencies import get_admin_user
from events_app.db.database import engine
from events_app.core.config import settings
from events_app.core import exceptions
from events_app.db.admin import (
    CategoryAdmin,
    EventAdmin,
    LocationAdmin,
    SourceUserAdmin,
    TagAdmin,
    UserAdmin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache_redis_client = aioredis.from_url(
        f"redis://{REDIS_CACHE_HOST}:{REDIS_CACHE_PORT}/0",
        encoding="utf8",
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(cache_redis_client), prefix="fastapi-cache")

    yield

    await app.state.cache_redis_client.close()


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory='static'), name='static')
REDIS_CACHE_HOST = settings.REDIS_CACHE_HOST
REDIS_CACHE_PORT = settings.REDIS_CACHE_PORT

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def admin_protect_middleware(request: Request, call_next):
    if request.url.path.startswith("/admin"):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Forbidden"}
                )
            token = auth_header.split(" ")[1]
            await get_admin_user(token=token)
        except Exception:
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden"}
            )
    return await call_next(request)


admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(EventAdmin)
admin.add_view(LocationAdmin)
admin.add_view(SourceUserAdmin)
admin.add_view(TagAdmin)

main_api_router = APIRouter(prefix="/api")
main_api_router.include_router(api.categories_router)
main_api_router.include_router(api.events_router)
main_api_router.include_router(api.locations_router)
main_api_router.include_router(api.tags_router)
main_api_router.include_router(api.users_router)

app.include_router(main_api_router)


@app.exception_handler(exceptions.UnauthorizedException)
async def unauthorized_exception_handler(
    request: Request,
    exc: exceptions.UnauthorizedException
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
    )


@app.exception_handler(exceptions.ForbiddenException)
async def forbidden_exception_handler(
    request: Request,
    exc: exceptions.ForbiddenException
):
    return JSONResponse(
        status_code=403,
        content={"detail": "Forbidden"},
    )


@app.exception_handler(exceptions.NotFoundException)
async def not_found_exception_handler(
    request: Request,
    exc: exceptions.NotFoundException
):
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"},
    )


@app.exception_handler(exceptions.BadRequestException)
async def bad_request_exception_handler(
    request: Request,
    exc: exceptions.BadRequestException
):
    content = exc.detail if isinstance(
        exc.detail, dict
        ) else {"detail": exc.detail}
    return JSONResponse(
        status_code=400,
        content=content,
    )


@app.exception_handler(exceptions.NoContentException)
async def no_content_exception_handler(
    request: Request,
    exc: exceptions.NoContentException
):
    return JSONResponse(
        status_code=204,
        content=None,
    )


if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)
