import json
import pathlib

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def dump_schema(app: FastAPI) -> None:
    file = pathlib.Path("openapi.json")
    with file.open('w') as f:
        json.dump(get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ), f)


if __name__ == '__main__':
    from main import app
    dump_schema(app)
