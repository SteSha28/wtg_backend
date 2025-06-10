from datetime import date
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    StringConstraints,
)

from .events import EventShort

UsernameStr = Annotated[
    str,
    StringConstraints(min_length=3, max_length=20, ),
]
NameStr = Annotated[
    str,
    StringConstraints(max_length=32, pattern=r"^[^\d]*$", ),
]


def validate_password(password: str):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(ch.isalpha() for ch in password):
        raise ValueError("Password must contain at least one letter")
    if not any(ch.isdigit() for ch in password):
        raise ValueError("Pasword must contain at least one digit")
    return password


class UserCreate(BaseModel):
    username: UsernameStr = Field(...,)
    email: EmailStr = Field(...,)
    password: str = Field(...,)

    @field_validator('password')
    def validate(cls, v):
        return validate_password(v)


class UserBase(BaseModel):
    id: int
    username: UsernameStr | None = None
    email: EmailStr | None = None
    first_name: NameStr | None = None
    last_name: NameStr | None = None
    dob: date | None = None
    gender: Literal["male", "female", "not_specified"] = "not_specified"
    description: str | None = None
    profile_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserFromDB(UserBase):
    is_admin: bool
    hashed_password: str
    source_id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    ...


class UserWithFavorites(UserBase):
    favorites: list[EventShort]

    model_config = ConfigDict(from_attributes=True)


class AvatarResponce(BaseModel):
    profile_image: str


class PasswordChange(BaseModel):
    last_password: str
    password: str

    @field_validator('password')
    def validate(cls, v):
        return validate_password(v)


class TokenResponce(BaseModel):
    Authorization: str
    token_type: str = "Bearer"
    id: int


class SourceUserCreate(BaseModel):
    name: str
    description: str


class SourceUserFromDB(SourceUserCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
