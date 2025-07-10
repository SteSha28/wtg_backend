from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import (
    BaseModel, ConfigDict,
    field_validator, FutureDatetime,
    HttpUrl,
)


class LocationCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    description: str


class LocationShort(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class LocationFromDB(LocationCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str
    plural_name: Optional[str] = None


class CategoryFromDB(CategoryCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str
    description: str


class TagFromDB(TagCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EventDateSchema(BaseModel):
    id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    title: str
    description: str
    dates: list[FutureDatetime]
    url: HttpUrl
    price: str
    location_id: int
    tags: list[int]
    category_id: Optional[int]

    @field_validator('url')
    def convert_url_to_string(cls, v):
        return str(v)


class EventShort(BaseModel):
    id: int
    title: str
    location: LocationShort
    closest_date: datetime
    event_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventFromDB(BaseModel):
    id: int
    title: str
    description: str
    closest_date: datetime
    url: HttpUrl
    price: str
    event_image: Optional[str] = None

    location: LocationFromDB
    tags: list[TagFromDB] = []
    category: Optional[CategoryFromDB] = None
    dates: List[EventDateSchema]

    model_config = ConfigDict(from_attributes=True)


class SearchResult(BaseModel):
    id: int
    name: str
    type: str


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    offset: int
    limit: int
    items: List[T]
