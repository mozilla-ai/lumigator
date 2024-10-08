from fastapi import APIRouter
from backend.api.deps import MistralCompletionServiceDep, OpenAICompletionServiceDep
from schemas.completions import CompletionRequest
from loguru import logger

router = APIRouter()

MISTRAL = "mistral"
OPENAI = "openai"


@router.get("/")
def list_vendors():
    return [MISTRAL, OPENAI]


@router.post(f"/{MISTRAL}")
def get_mistral_completion(request: CompletionRequest, service: MistralCompletionServiceDep):
    return service.get_completions_response(request)


@router.post(f"/{OPENAI}")
def get_openai_completion(request: CompletionRequest, service: OpenAICompletionServiceDep):
    return service.get_completions_response(request)
