import json
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from backend.main import app

openapi_path = Path('../../docs/source/specs/openapi.json')
with openapi_path.open('w') as f:
    json.dump(get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
        # openapi_prefix=app.openapi_prefix,
    ), f)

