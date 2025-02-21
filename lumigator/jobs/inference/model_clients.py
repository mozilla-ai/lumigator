import re
from abc import abstractmethod

from inference_config import InferenceJobConfig
from litellm import completion
from loguru import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from transformers import GenerationConfig as HFGenerationConfig


def strip_path_prefix(path: str) -> str:
    """Strip the 'scheme://' prefix from the start of a string."""
    pattern = "^\w+\:\/\/"
    return re.sub(pattern, "", path)


class BaseModelClient:
    """Abstract class for a model client, used to provide a uniform interface
    (currentnly just a simple predict method) to models served in different
    ways (e.g. HF models loaded locally, OpenAI endpoints, vLLM inference
    servers, llamafile).
    """

    @abstractmethod
    def __init__(self, model: str, config: InferenceJobConfig):
        """Used to initialize the model / inference service."""
        pass

    @abstractmethod
    def predict(self, prompt: str) -> str:
        """Given a prompt, return a prediction."""
        pass


class LiteLLMModelClient(BaseModelClient):
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

    def __init__(self, config: InferenceJobConfig):
        self.config = config
        self.system = "You are a helpful assisant., please summarize the given input."
        logger.info(f"LiteLLMModelClient initialized with config: {config}")

    def predict(
        self,
        prompt: str,
    ) -> str:
        litellm_model = f"{self.config.inference_server.provider}/{self.config.inference_server.model}"
        logger.info(f"Sending request to {litellm_model}")
        response = completion(
            model=litellm_model,
            messages=[
                {"role": "system", "content": self.system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.config.generation_config.max_tokens,
            frequency_penalty=self.config.generation_config.frequency_penalty,
            temperature=self.config.generation_config.temperature,
            top_p=self.config.generation_config.top_p,
            drop_params=True,
            api_base=self.config.inference_server.base_url if self.config.inference_server else None,
        )
        # LiteLLM gives us the cost of each API which is nice.
        # Eventually we can add this to the response object as well.
        cost = response._hidden_params["response_cost"]
        logger.info(f"Response cost: {cost}")
        return response.choices[0].message.content


class HuggingFaceSeq2SeqPipeline(BaseModelClient):
    def __init__(self, config: InferenceJobConfig):
        self.config = config
        hf_pipeline = config.hf_pipeline
        # The summarization pipeline is only supported for Seq2Seq models
        # https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.SummarizationPipeline
        try:
            model = AutoModelForSeq2SeqLM.from_pretrained(
                hf_pipeline.model_name_or_path,
                trust_remote_code=hf_pipeline.trust_remote_code,
                torch_dtype=hf_pipeline.torch_dtype,
            )
        except ValueError as e:
            raise ValueError(
                f"Model {hf_pipeline.model_name_or_path} is not a Seq2Seq model. "
                "Only Seq2Seq models are supported for the summarization pipeline."
            ) from e
        tokenizer = AutoTokenizer.from_pretrained(
            hf_pipeline.model_name_or_path,
            use_fast=hf_pipeline.use_fast,
            trust_remote_code=hf_pipeline.trust_remote_code,
        )

        # The reason I create the models and tokenizers separately is so that I can validate the model type
        # before creating the pipeline. This way I can give a more helpful error message and stack trace
        self._pipeline = pipeline(
            task=hf_pipeline.task,
            model=model,
            tokenizer=tokenizer,
            revision=hf_pipeline.revision,
            device=hf_pipeline.device,
        )
        self._set_max_length()
        logger.info(f"HuggingFaceSeq2SeqPipeline initialized with config: {config}")

    def _set_max_length(self):
        """Make sure that the model can actually support the max_tokens configured.
        For the Seq2Seq models, the max_length is the max_position_embeddings. That's because the input and output
        tokens have separate positions, so the model can generate upto max_position_embeddings tokens.
        This isn't true if it's a CausalLM model, since the output token positions would be len(input) + len(output).
        """
        max_length = self._pipeline.model.config.max_position_embeddings
        # If the model is of the HF Hub the odds of this being wrong are low, but it's still good to check that the
        # tokenizer model and the model have the same max_position_embeddings
        if self._pipeline.tokenizer.model_max_length != max_length:
            logger.warning(
                f"Tokenizer max_length ({self._pipeline.tokenizer.model_max_length})"
                f" and model max_position_embeddings ({max_length}) do not match."
                " This could lead to unexpected behavior, make sure this is intended."
            )
        if self.config.generation_config.max_tokens:
            if self.config.generation_config.max_tokens > max_length:
                raise ValueError(
                    f"Model can generate {max_length} tokens.Requested {self.config.generation_config.max_tokens}."
                )
            else:
                logger.info(f"Setting max_length to {self.config.generation_config.max_tokens}")
                self.config.generation_config.max_tokens = self.config.generation_config.max_tokens
        else:
            logger.info(
                f"Setting max_length to the max supported length by the model by its position embeddings: {max_length}"
            )
            self.config.generation_config.max_tokens = max_length

    def predict(self, prompt):
        prediction = self._pipeline(
            prompt,
            truncation=True,
            generation_config=HFGenerationConfig(**self.config.generation_config.model_dump()),
        )[0]
        # The result is a dictionary with a single key, which name depends on the task
        # (e.g., 'summary_text' for summarization)
        # Get the name of the key and return its value
        result_key = list(prediction.keys())[0]
        return prediction[result_key]
