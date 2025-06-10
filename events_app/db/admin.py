from sqladmin import ModelView
from .models import (
    Category,
    Event,
    Location,
    SourceUser,
    Tag,
    User,
)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]


class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.name]


class EventAdmin(ModelView, model=Event):
    column_list = [Event.id, Event.title]


class LocationAdmin(ModelView, model=Location):
    column_list = [Location.id, Location.name]


class SourceUserAdmin(ModelView, model=SourceUser):
    column_list = [SourceUser.id, SourceUser.name]


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name]
