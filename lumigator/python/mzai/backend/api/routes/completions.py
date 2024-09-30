from fastapi import APIRouter

from mzai.backend.api.deps import MistralCompletionServiceDep, OpenAICompletionServiceDep
from mzai.schemas.completions import CompletionRequest

router = APIRouter()


@router.get("/")
def list_vendors():
    return ["openai", "mistral"]


@router.post("/mistral")
def get_mistral_completion(request: CompletionRequest, service: MistralCompletionServiceDep):
    return service.get_completions_response(request)


@router.post("/openai")
def get_openai_completion(request: CompletionRequest, service: OpenAICompletionServiceDep):
    return service.get_completions_response(request)
