from pydantic import BaseModel
from ray import serve
from ray.serve import Application
from starlette.requests import Request
from transformers import AutoModelForSeq2SeqLM, pipeline


class SummarizerArgs(BaseModel):
    name: str  # model name, but model is protected namespace in pydantic
    tokenizer: str
    task: str
    description: str


@serve.deployment()
class Summarizer:
    def __init__(self, name: str, tokenizer: str, task: str):
        # Load model
        model = AutoModelForSeq2SeqLM.from_pretrained(
            pretrained_model_name_or_path=name,
            trust_remote_code=True,
        )
        self.model = pipeline(task, model=model, tokenizer=tokenizer)

    def summarize(self, text: str) -> str:
        # Run inference
        model_output = self.model(text)

        # Post-process output to return only the summary text
        summary = model_output[0]["summary_text"]

        return summary

    async def __call__(self, http_request: Request) -> dict[str, str]:
        text: str = await http_request.json()
        summary = self.summarize(text["text"])

        return {"result": summary}


def app(args: SummarizerArgs) -> Application:
    return Summarizer.bind(args.name, args.tokenizer, args.task, args.description)
