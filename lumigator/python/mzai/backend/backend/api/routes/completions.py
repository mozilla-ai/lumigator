from fastapi import APIRouter
from schemas.completions import CompletionRequest, CompletionResponse

from backend.api.deps import MistralCompletionServiceDep, OpenAICompletionServiceDep

router = APIRouter()


@router.get("/")
def list_vendors() -> list[str]:
    return ["openai", "mistral"]


@router.post("/mistral")
def get_mistral_completion(
    request: CompletionRequest, service: MistralCompletionServiceDep
) -> CompletionResponse:
    return service.get_completions_response(request)


@router.post("/openai")
def get_openai_completion(
    request: CompletionRequest, service: OpenAICompletionServiceDep
) -> CompletionResponse:
    return service.get_completions_response(request)
