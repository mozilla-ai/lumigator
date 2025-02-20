from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.keys import Key
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import KeyServiceDep
from backend.services.exceptions.base_exceptions import ServiceError

router = APIRouter()


def key_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {}


@router.put(
    "/{key_name}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_201_CREATED: {"description": "Dataset successfully uploaded"},
    },
)
def upload_key(
    service: KeyServiceDep,
    key: Key,
    key_name: str,
    request: Request,
    response: Response,
) -> None:
    """Uploads a key for use in Lumigator.

    Lumigator uses different keys for purposes such as external API calls.
    The user can upload new values for these keys, but they cannot retrieve
    them.
    """
    service.upload_key(key, key_name)
