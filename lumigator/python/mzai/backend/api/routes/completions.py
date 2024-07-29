from fastapi import APIRouter
from mzai.backend.services.completions import MistralCompletionService
from mzai.schemas.completions import CompletionResponse, CompletionRequest
from loguru import logger

router = APIRouter()


@router.post("/mistral")
def get_mistral_completion(
    text: CompletionRequest, service: MistralCompletionService
) -> CompletionResponse:
    return service.get_completions_response(text)
