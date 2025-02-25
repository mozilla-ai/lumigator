import re
from abc import abstractmethod

from inference_config import InferenceJobConfig
from litellm import completion
from loguru import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


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
        self.system_prompt = self.config.inference_server.system_prompt
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
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_new_tokens=self.config.generation_config.max_new_tokens,
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


class HuggingFaceModelClient(BaseModelClient):
    def __init__(self, config: InferenceJobConfig):
        self._config = config
        self._system = config.system_prompt
        self._task = config.hf_pipeline.task
        if self._task == "summarization":
            # The summarization pipeline is only supported for Seq2Seq models
            # https://huggingface.co/docs/transformers/en/main_classes/pipelines#transformers.SummarizationPipeline
            try:
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    config.hf_pipeline.model_name_or_path,
                    trust_remote_code=config.hf_pipeline.trust_remote_code,
                    torch_dtype=config.hf_pipeline.torch_dtype,
                )
            except ValueError as e:
                raise ValueError(
                    f"Model {config.hf_pipeline.model_name_or_path} is not a Seq2Seq model. "
                    "Only Seq2Seq models are supported for the summarization pipeline."
                ) from e
            logger.info(f"System prompt: {config.system_prompt}")
            # Store this so we can check if the input prompt is too long
            self.tokenizer = AutoTokenizer.from_pretrained(
                config.hf_pipeline.model_name_or_path,
                use_fast=config.hf_pipeline.use_fast,
                trust_remote_code=config.hf_pipeline.trust_remote_code,
            )

            # The reason I create the models and tokenizers separately is so that I can validate the model type
            # before creating the pipeline. This way I can give a more helpful error message and stack trace
            self._pipeline = pipeline(
                task=config.hf_pipeline.task,
                model=model,
                tokenizer=self.tokenizer,
                revision=config.hf_pipeline.revision,
                device=config.hf_pipeline.device,
            )
            self._set_max_length()
            logger.info(f"HuggingFaceModelClient initialized with config: {config}")
        elif self._task == "text-generation":
            self._system = config.system_prompt
            self._pipeline = pipeline(**config.hf_pipeline.model_dump())
        else:
            raise ValueError(f"Unsupported task: {self._task}")

    def _set_max_length(self):
        """Make sure that the model can actually support the max_new_tokens configured.
        For the Seq2Seq models, the max_length is the max_position_embeddings. That's because the input and output
        tokens have separate positions, so the model can generate upto max_position_embeddings tokens.
        This isn't true if it's a CausalLM model, since the output token positions would be len(input) + len(output).
        """
        max_pos_emb = self._pipeline.model.config.max_position_embeddings
        # If the model is of the HF Hub the odds of this being wrong are low, but it's still good to check that the
        # tokenizer model and the model have the same max_position_embeddings
        if self._pipeline.tokenizer.model_max_length != max_pos_emb:
            logger.warning(
                f"Tokenizer max_length ({self._pipeline.tokenizer.model_max_length})"
                f" and model max_position_embeddings ({max_pos_emb}) do not match."
                "Setting the tokenizer model_max_length to the model's max_position_embeddings."
            )
            self._pipeline.tokenizer.model_max_length = max_pos_emb
        if self._config.generation_config.max_new_tokens:
            if self._config.generation_config.max_new_tokens > max_pos_emb:
                logger.warning(
                    f"Model can generate {max_pos_emb} tokens."
                    f" Requested {self._config.generation_config.max_new_tokens}."
                    f" Setting max_length to {max_pos_emb}."
                )
                self._config.generation_config.max_new_tokens = max_pos_emb
            else:
                logger.info(f"Setting max_length to {self._config.generation_config.max_new_tokens}")
        else:
            logger.info(
                f"Setting max_length to the max supported length by the model by its position embeddings: {max_pos_emb}"
            )
            self._config.generation_config.max_new_tokens = max_pos_emb

    def predict(self, prompt):
        # When using a text-generation model, the pipeline returns a dictionary with a single key,
        # 'generated_text'. The value of this key is a list of dictionaries, each containing the\
        # role and content of a message. For example:
        # [{'role': 'system', 'content': 'You are a helpful assistant.'},
        #  {'role': 'user', 'content': 'What is the capital of France?'}, ...]
        # We want to return the content of the last message in the list, which is the model's
        # response to the prompt.
        if self._task == "text-generation":
            messages = [
                {"role": "system", "content": self._system},
                {"role": "user", "content": prompt},
            ]
            generation = self._pipeline(messages, max_new_tokens=self._config.generation_config.max_new_tokens)[0]
            return generation["generated_text"][-1]["content"]

        # If we're using a summarization model, the pipeline returns a dictionary with a single key.
        # The name of the key depends on the task (e.g., 'summary_text' for summarization).
        # Get the name of the key and return its value.
        if self._task == "summarization":
            generation = self._pipeline(
                prompt, max_new_tokens=self._config.generation_config.max_new_tokens, truncation=True
            )[0]
            return generation["summary_text"]
