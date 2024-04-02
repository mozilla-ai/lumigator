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


def aiopenapigen():
    import aiopenapi3
    from aiopenapi3.loader import FileSystemLoader
    from pathlib import Path

    a = FileSystemLoader(Path(base="./openapi.json"))
    api = aiopenapi3.OpenAPI.load_file("https://localhost/apispect",
                                     path=Path("./openapi.json"),
                                     loader=a)


    operationIds = list(api._.Iter(api, False))
    print(operationIds)



if __name__ == '__main__':
    # from main import app
    aiopenapigen()
