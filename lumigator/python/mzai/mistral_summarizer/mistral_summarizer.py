import logging

from pydantic import BaseModel
from ray import serve
from ray.serve import Application
from starlette.requests import Request
from transformers import AutoModelForCausalLM, pipeline, AutoTokenizer

logger = logging.getLogger("ray.serve")


class SummarizerArgs(BaseModel):
    name: str  # model name, but model is protected namespace in pydantic
    tokenizer: str
    description: str


@serve.deployment()
class MistralSummarizer:
    def __init__(self, name: str, tokenizer: str):
        import torch  # Import torch here so it's not a dependency on the backend

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=name,
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)

        self.device = (0 if torch.cuda.is_available() else -1,)

    def summarize(self, text: str) -> str:
        try:
            logger.info(f"Using HF model invocation. Model: {self.name}")
            inputs = self.tokenizer(
                f"Please summarize the following {text}",
                truncation=True,
                padding=True,
                return_tensors="pt",
            ).to(self.device)
            generated_ids = self.model.generate(**inputs, max_new_tokens=256)
            model_output: list[dict[str, str]] = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]
            return model_output
        except Exception:
            logger.error("No summary text")
            return ""

    async def __call__(self, http_request: Request) -> dict[str, str]:
        text: list[str] = await http_request.json()
        # Assume input is list of text documents
        summary = self.summarize(text["text"])

        return {"result": summary}


# def app(args: Dict[str, str]) -> Application:
def app(args: SummarizerArgs) -> Application:
    logger.info("Mistral Summarizer is running")
    logger.info(args)
    return MistralSummarizer.bind(args.name, args.tokenizer, args.task)  # args.description unused
