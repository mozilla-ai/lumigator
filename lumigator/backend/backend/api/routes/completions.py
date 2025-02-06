from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.completions import CompletionRequest

from backend.api.deps import CompletionServiceDep
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.completion_exceptions import CompletionUpstreamError

router = APIRouter()

VENDOR_MISTRAL = "mistral"
VENDOR_OPENAI = "openai"


def completion_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        CompletionUpstreamError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }


@router.post("/")
def get_completion(request: CompletionRequest, service: CompletionServiceDep) -> dict:
    return service.get_completions_response(request)
