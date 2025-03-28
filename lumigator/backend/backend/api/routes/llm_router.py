import requests
from fastapi import APIRouter, Query
from litellm import completion

from backend.api.deps import SecretServiceDep

router = APIRouter()


@router.get("/")
def route_prompt(
    secret_service: SecretServiceDep,
    prompt: str = Query(..., description="The prompt to be routed"),
    threshold: float = Query(0.5, description="Routing threshold value between 0 and 1"),
    router_url: str = Query(..., description="The URL of the model to route to."),
    dry_run: bool = Query(False, description="Whether to route the request or not."),
):
    params = {"prompt": prompt, "threshold": threshold, "strong_model": "gpt-4o", "weak_model": "gpt-4o-mini"}

    response = requests.get(f"{router_url}/route", params=params)
    result = response.json()

    if not dry_run:
        model = f"openai/{result['routed_model']}"
        client = LiteLLMModelClient(secret_service)
        examples = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        return client.make_completion_request(model, examples)

    return result


class LiteLLMModelClient:
    """Model client for models served via openai-compatible API.
    For OpenAI models:
    - The base_url is fixed
    - Choose an model name (see https://platform.openai.com/docs/models)
    - Customize the system prompt if needed

    For compatible models:
    - Works with local/remote vLLM-served models and llamafiles
    - Provide base_url and model
    - Customize the system prompt if needed
    """

    def __init__(self, secret_service: SecretServiceDep) -> None:
        self.api_key = secret_service.get_decrypted_secret_value("openai_api_key")

    def make_completion_request(self, litellm_model: str, examples: list[dict[str, str]]):
        """Make a request to the LLM with proper error handling"""
        return completion(
            model=litellm_model,
            messages=examples,
            api_key=self.api_key,
        )
