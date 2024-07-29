import logging

from pydantic import BaseModel, Field
from ray import serve
from ray.serve import Application
from starlette.requests import Request
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

logger = logging.getLogger("ray.serve")


class CausalSummarizerArgs(BaseModel):
    name: str  # model name, but model is protected namespace in pydantic
    tokenizer: str
    task: str
    description: str


@serve.deployment()
class CausalSummarizer:
    def __init__(self, name: str, tokenizer: str, task: str):
        import torch  # Import torch here to avoid backend dependency

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(name, trust_remote_code=True)

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)

        self.pipe = pipeline(
            task=task,
            model=self.model,
            tokenizer=self.tokenizer,
        )

        self.device = (0 if torch.cuda.is_available() else -1,)

    def summarize(self, text: str) -> str:
        messages = [
            {
                "role": "system",
                "content": f"You are a chatbot who is friendly and helps to summarize text! {text}",
            },
            {"role": "user", "content": "Summarize the following text"},
        ]

        generation_args = {
            "max_new_tokens": 500,
            "return_full_text": False,
            "temperature": 0.0,
            "do_sample": False,
        }

        try:
            logger.info(f"Using Pipeline")

            output = pipeline(messages, **generation_args)
            return output[0]["generated_text"]
        except Exception:
            logger.error("No summary text")
            return ""

    async def __call__(self, http_request: Request) -> dict[str, str]:
        text: list[str] = await http_request.json()
        # Assume input is list of text documents
        summary = self.summarize(text["text"])

        return {"result": summary}


def app(args: CausalSummarizerArgs) -> Application:
    logger.info(f"{args.name} Summarizer is running")
    logger.info(args)
    return CausalSummarizer.bind(args.name, args.tokenizer, args.task)
