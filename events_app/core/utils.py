from starlette.requests import Request


def custom_key_builder(
        func,
        namespace,
        request: Request,
        response,
        *args, **kwargs):
    query = str(request.query_params)
    key = f"{namespace}:{request.url.path}?{query}"

    return key
