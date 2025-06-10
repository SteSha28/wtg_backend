class UnauthorizedException(Exception):
    pass


class ForbiddenException(Exception):
    pass


class NotFoundException(Exception):
    pass


class BadRequestException(Exception):
    def __init__(self, detail: str | dict = "Bad request"):
        self.detail = detail


class NoContentException(Exception):
    pass
