from fastapi import APIRouter
from backend.api.deps import MistralCompletionServiceDep, OpenAICompletionServiceDep
from schemas.completions import CompletionRequest
from loguru import logger

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
def get_openai_completion(request: CompletionRequest, service: OpenAICompletionServiceDep):
    return service.get_completions_response(request)
