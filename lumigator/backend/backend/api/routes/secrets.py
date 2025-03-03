from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.secrets import SecretGetRequest, SecretUploadRequest
from starlette.requests import Request
from starlette.responses import Response

from backend.api.deps import SecretServiceDep
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.secret_exceptions import SecretDecryptionError, SecretEncryptionError

router = APIRouter()


def secret_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        SecretDecryptionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        SecretEncryptionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }


@router.get("/")
def list_secrets(service: SecretServiceDep) -> list[SecretGetRequest]:
    """Lists all API configured secret names (and descriptions) stored in Lumigator."""
    return service.list_secrets()


@router.put(
    "/{secret_name}",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Secret successfully created"},
        status.HTTP_204_NO_CONTENT: {"description": "Secret successfully updated"},
    },
)
def upload_secret(
    service: SecretServiceDep,
    secret_upload_request: SecretUploadRequest,
    request: Request,
    response: Response,
    secret_name: str,
) -> None:
    """Uploads a secret for use in Lumigator.

    Lumigator uses different secrets for purposes such as external API calls.
    The user can upload new values for these secrets, but they cannot retrieve
    those values.
    """
    # Ensure we validate the secret name using our models.
    SecretGetRequest(name=secret_name, **secret_upload_request.model_dump())

    is_created = service.upload_secret(secret_name, secret_upload_request)
    if is_created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_204_NO_CONTENT
