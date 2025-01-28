from http import HTTPStatus

from fastapi import APIRouter, status
from lumigator_schemas.completions import CompletionRequest

from backend.api.deps import MistralCompletionServiceDep, OpenAICompletionServiceDep
from backend.services.exceptions.base_exceptions import ServiceError
from backend.services.exceptions.completion_exceptions import CompletionUpstreamError

router = APIRouter()

VENDOR_MISTRAL = "mistral"
VENDOR_OPENAI = "openai"


def completion_exception_mappings() -> dict[type[ServiceError], HTTPStatus]:
    return {
        CompletionUpstreamError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }


@router.get("/")
def list_vendors():
    return [VENDOR_MISTRAL, VENDOR_OPENAI]


@router.post(f"/{VENDOR_MISTRAL}")
def get_mistral_completion(request: CompletionRequest, service: MistralCompletionServiceDep):
    return service.get_completions_response(request)


@router.post(f"/{VENDOR_OPENAI}")
def get_openai_completion(request: CompletionRequest, service: OpenAICompletionServiceDep):
    return service.get_completions_response(request)
