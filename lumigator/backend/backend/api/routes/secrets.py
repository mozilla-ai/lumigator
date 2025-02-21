from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.secrets import Secret
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import SecretServiceDep
from backend.services.exceptions.base_exceptions import ServiceError

router = APIRouter()


def secret_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {}


@router.put(
    "/{secret_name}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_201_CREATED: {"description": "Dataset successfully uploaded"},
    },
)
def upload_secret(
    service: SecretServiceDep,
    secret: Secret,
    secret_name: str,
    request: Request,
    response: Response,
) -> None:
    """Uploads a secret for use in Lumigator.

    Lumigator uses different secrets for purposes such as external API calls.
    The user can upload new values for these secrets, but they cannot retrieve
    them.
    """
    service.upload_secret(secret, secret_name)
