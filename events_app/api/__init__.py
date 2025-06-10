from .categories import categories_router
from .events import events_router
from .locations import locations_router
from .users import users_router
from .tags import tags_router

__all__ = [
    'categories_router',
    'events_router',
    'locations_router',
    'users_router',
    'tags_router',
]
