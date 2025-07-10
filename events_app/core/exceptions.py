class UnauthorizedException(Exception):
    """Ошибка: доступ неавторизован (401 Unauthorized)."""
    pass


class ForbiddenException(Exception):
    """Ошибка: доступ запрещён (403 Forbidden)."""
    pass


class NotFoundException(Exception):
    """Ошибка: ресурс не найден (404 Not Found)."""
    pass


class BadRequestException(Exception):
    """Ошибка: некорректный запрос (400 Bad Request)."""
    def __init__(self, detail: str | dict = "Bad request"):
        self.detail = detail


class NoContentException(Exception):
    """Ошибка: нет содержимого для ответа (204 No Content)."""
    pass
