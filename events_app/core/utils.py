from starlette.requests import Request


def custom_key_builder(
        func,
        namespace,
        request: Request,
        response,
        *args, **kwargs):
    """
    Строит ключ для кеша на основе namespace и URL запроса с параметрами.

    Args:
        - func: Функция, для которой строится ключ (не используется).
        - namespace: Пространство имён кеша.
        - request (Request): Объект HTTP запроса.
        - response: Объект HTTP ответа (не используется).
        - *args: Дополнительные позиционные аргументы.
        - **kwargs: Дополнительные именованные аргументы.

    Returns:
        - str: Сформированный ключ кеша в формате "namespace:path?query".
    """
    query = str(request.query_params)
    key = f"{namespace}:{request.url.path}?{query}"

    return key
