from fastapi import APIRouter
from lumigator_schemas.completions import CompletionRequest

from backend.api.deps import LiteLLMCompletionServiceDep, MistralCompletionServiceDep

router = APIRouter()

VENDOR_MISTRAL = "mistral"
VENDOR_OPENAI = "openai"


@router.get("/")
def list_vendors():
    return [VENDOR_MISTRAL, VENDOR_OPENAI]


@router.post(f"/{VENDOR_MISTRAL}")
def get_mistral_completion(request: CompletionRequest, service: MistralCompletionServiceDep):
    return service.get_completions_response(request)


@router.post(f"/{VENDOR_OPENAI}")
def get_openai_completion(request: CompletionRequest, service: LiteLLMCompletionServiceDep):
    return service.get_completions_response(request)
