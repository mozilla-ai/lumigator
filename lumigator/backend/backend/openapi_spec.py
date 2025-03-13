import argparse
import json
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from backend.main import app


def dump_openapi(dst: str) -> None:
    openapi_path = Path(dst)
    with openapi_path.open("w") as f:
        json.dump(
            get_openapi(
                title=app.title,
                version=app.version,
                openapi_version=app.openapi_version,
                description=app.description,
                routes=app.routes,
            ),
            f,
        )


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("target_path", help="path to store the openapi spec (overwrites contents if present)")
    return parser


if __name__ == "__main__":
    parser = build_argparser()
    args = parser.parse_args()
    dump_openapi(args.target_path)
