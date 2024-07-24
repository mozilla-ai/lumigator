import logging

from pydantic import BaseModel
from ray import serve
from ray.serve import Application
from starlette.requests import Request
from transformers import AutoModelForSeq2SeqLM, AutoModelForCausalLM, pipeline
from transformers.models.auto import AutoConfig, AutoTokenizer

from transformers.models.auto.modeling_auto import (
    MODEL_FOR_CAUSAL_LM_MAPPING_NAMES,
    MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES,
)

logger = logging.getLogger("ray.serve")


class SummarizerArgs(BaseModel):
    name: str  # model name, but model is protected namespace in pydantic
    tokenizer: str
    task: str
    description: str


@serve.deployment()
class Summarizer:
    def __init__(self, name: str, tokenizer: str, task: str):
        import torch  # noqa

        self.model_config = AutoConfig.from_pretrained(name)

        # Select between BART and Mistral model classes
        if self.model_config.model_type in MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES:
            self.model_class = AutoModelForSeq2SeqLM
        elif self.model_config.model_type in MODEL_FOR_CAUSAL_LM_MAPPING_NAMES:
            self.model_class = AutoModelForCausalLM
        else:
            logger.info("Model type not supported. Trying AutoModelForSeq2SeqLM")
            self.model_class = AutoModelForSeq2SeqLM

        # Load model
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            pretrained_model_name_or_path=name,
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=tokenizer,
            trust_remote_code=True,
        )

        self.device = 0 if torch.cuda.is_available() else -1

        self.pipe = pipeline(
            task=task,
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )

    def summarize(self, text: str) -> str:
        try:
            if self.model_config.evaluation.use_pipeline:
                logger.info(f"Using summarization pipeline. Model: {self.name}")
                #  List or list[list[`dict`]] with `summary_text` and `summary_token_ids` as keys
                model_output: list[dict[str, str]] = self.pipe(text, min_length=30)[0][
                    "summary_text"
                ]
            else:
                logger.info(f"Using direct HF model invocation. Model: {self.name}")
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
        # TODO: Change input to string
        summary = self.summarize(text["text"])

        return {"result": summary}


def app(args: SummarizerArgs) -> Application:
    logger.info("Summarizer is running")
    logger.info(args)
    return Summarizer.bind(args.name, args.tokenizer, args.task)  # args.description unused
