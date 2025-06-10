from fastapi import (
    HTTPException,
    status,
)
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError

from .config import settings

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_jwt_token(data: dict):
    to_encode = data.copy()
    return encode(to_encode,
                  settings.SECRET_KEY,
                  algorithm=settings.ALGORITHM)


def get_current_user_id(token) -> int:
    try:
        payload = decode(token,
                         settings.SECRET_KEY,
                         algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except InvalidTokenError:
        raise credentials_exception
