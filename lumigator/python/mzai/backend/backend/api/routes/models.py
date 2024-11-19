from fastapi import APIRouter, HTTPException
from lumigator_schemas.extras import ListingResponse

SUPPORTED_TASKS = ["summarization"]

SUGGESTED_MODELS = [
    {
        "name:": "facebook/bart-large-cnn",
        "uri": "hf://facebook/bart-large-cnn",
        "description": "BART is a large-sized model fine-tuned on the CNN Daily Mail dataset.",
    },
    {
        "name": "mikeadimech/longformer-qmsum-meeting-summarization",
        "uri": "hf://mikeadimech/longformer-qmsum-meeting-summarization",
        "description": (
            "Longformer is a transformer model that is capable of processing long sequences."
        ),
    },
    {
        "name": "mrm8488/t5-base-finetuned-summarize-news",
        "uri": "hf://mrm8488/t5-base-finetuned-summarize-news",
        "description": (
            "Google's T5 base fine-tuned on News Summary dataset for summarization downstream task."
        ),
    },
    {
        "name": "Falconsai/text_summarization",
        "uri": "hf://Falconsai/text_summarization",
        "description": (
            "A fine-tuned variant of the T5 transformer model, designed for the task "
            "of text summarization."
        ),
    },
    {
        "name": "mistralai/Mistral-7B-Instruct-v0.3",
        "uri": "hf://mistralai/Mistral-7B-Instruct-v0.3",
        "description": (
            "Mistral-7B-Instruct-v0.3 is an instruct fine-tuned version of the Mistral-7B-v0.3."
        ),
    },
    {
        "name": "gpt-4o-mini",
        "uri": "oai://gpt-4o-mini",
        "description": "OpenAI's GPT-4o-mini model.",
    },
    {
        "name": "gpt-4-turbo",
        "uri": "oai://gpt-4-turbo",
        "description": "OpenAI's GPT-4 Turbo model.",
    },
    {
        "name": "open-mistral-7b",
        "uri": "mistral://open-mistral-7b",
        "description": "Mistral's 7B model.",
    },
    {
        "name": "mistralai/Mistral-7B-Instruct-v0.2",
        "uri": "llamafile://mistralai/Mistral-7B-Instruct-v0.2",
        "description": "A llamafile package of Mistral's 7B Instruct model.",
    },
]

router = APIRouter()


@router.get("/{task_name}")
def get_suggested_models(task_name: str) -> ListingResponse[dict]:
    """Get a list of suggested models for the given task.

    Args:
        task_name (str): The task name.

    Returns:
        ListingResponse[str]: A list of suggested models.
    """
    # Currently, only summarization task is supported.
    if task_name != "summarization":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported task. Choose from: {SUPPORTED_TASKS}",
        )

    return_data = {
        "total": len(SUGGESTED_MODELS),
        "items": SUGGESTED_MODELS,
    }
    return ListingResponse[dict].model_validate(return_data)
