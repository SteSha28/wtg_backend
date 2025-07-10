from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хэширует пароль.

    Args:
        - password (str): Обычный текстовый пароль.

    Returns:
        - str: Хэшированный пароль.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли обычный пароль хэшированному.

    Args:
        - plain_password (str): Обычный пароль.
        - hashed_password (str): Хэшированный пароль.

    Returns:
        - bool: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)
