import os
import uuid

from fastapi import HTTPException

from .constants import (
    AVATAR_DIR,
    EVENTS_IMAGE_DIR,
)


os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(EVENTS_IMAGE_DIR, exist_ok=True)


async def upload_image(file, dir: str):
    """
    Загружает изображение в указанную директорию.

    Проверяет расширение файла, сохраняет с уникальным именем и
    возвращает путь.

    Args:
        - file: Загружаемый файл.
        - dir (str): Путь к директории для сохранения.

    Raises:
        - HTTPException: Если расширение файла некорректно.

    Returns:
        - dict: Словарь с ключом "image" и значением — путём к файлу.
    """
    file_extention = file.filename.split('.')[-1].lower()
    if file_extention not in ['png', 'jpg', 'jpeg']:
        raise HTTPException(
            status_code=400,
            detail='Invalid file type',
        )

    unique_filename = f'{uuid.uuid4()}.{file_extention}'
    file_path = os.path.join(dir, unique_filename)

    with open(file_path, 'wb') as buffer:
        content = await file.read()
        buffer.write(content)

    avatar_url = f'{dir}/{unique_filename}'
    return {"image": avatar_url}


def remove_file_if_exists(file_path: str):
    """
    Удаляет файл, если он существует.

    Args:
        - file_path (str): Путь к файлу.
    """
    if file_path and os.path.isfile(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
