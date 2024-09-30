import logging

from pydantic import BaseModel
from ray import serve
from ray.serve import Application
from starlette.requests import Request
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

logger = logging.getLogger("ray.serve")


class SummarizerArgs(BaseModel):
    name: str  # model name, but model is protected namespace in pydantic
    tokenizer: str
    task: str
    description: str


@serve.deployment()
class Summarizer:
    def __init__(self, name: str, tokenizer: str, task: str):
        import torch  # Import torch here so it's not a dependency on the backend

        # Load model
        model = AutoModelForSeq2SeqLM.from_pretrained(
            pretrained_model_name_or_path=name,
            trust_remote_code=True,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer, model_max_length=1024, truncate=True
        )
        self.pipe = pipeline(
            task,
            model=model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,
        )

    def summarize(self, text: str) -> str:
        #  A list or a list of list of `dict` with `summary_text` and `summary_token_ids` as keys
        # Setting max length of 1024 per bart context window size
        model_output: list[dict[str, str]] = self.pipe(
            text, min_length=30, max_length=1024, truncation=True, do_sample=False
        )

        try:
            summary = model_output[0]["summary_text"]
            return summary
        except Exception:
            logger.error("No summary text")
            return ""

    async def __call__(self, http_request: Request) -> dict[str, str]:
        text: list[str] = await http_request.json()
        # Assume input is list of text documents
        summary = self.summarize(text["text"])

        return {"result": summary}


def app(args: SummarizerArgs) -> Application:
    logger.info("Launching summarizer")
    logger.info(args)
    return Summarizer.bind(args.name, args.tokenizer, args.task)
