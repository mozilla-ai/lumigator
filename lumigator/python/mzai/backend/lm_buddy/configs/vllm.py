from lm_buddy.configs.common import LMBuddyConfig
from lm_buddy.paths import AssetPath


class InferenceServerConfig(LMBuddyConfig):
    """Generic configuration for an externally hosted inference endpoint.

    The inference server is defined by an endpoint with the provided `base_url`.
    The model `engine` powering the endpoint can also be specified
    to provide further metadata about the model used for inference
    (e.g., for generating W&B artifact lineages).

    Note: This configuration is intended to be generic and not bound to the interface
    of any specific training/evaluation framework. See `LocalChatCompletionConfig`
    or `vLLMCompletionsConfig` for intended usage alongside a third-party framework.
    """

    base_url: str
    engine: AssetPath

    # optional system prompt to be used by default in chat completions
    system_prompt: str | None = None

    # max number of retries when communication with server fails
    max_retries: int | None = None


class VLLMCompletionsConfig(LMBuddyConfig):
    """Configuration for a vLLM-based completions service

    The "local-chat-completions" model is powered by a self-hosted inference server,
    specified as an `InferenceServerConfig`. Additional arguments are also provided
    to control the tokenizer type and generation parameters.

    Note that this is just a subset of the parameters allowed by a vLLM server (see
    https://github.com/vllm-project/vllm/blob/main/vllm/sampling_params.py). If we
    choose to use this configuration to cover for more use cases, it will make sense
    to add the other supported configuration parameters too.
    """

    inference: InferenceServerConfig
    # vLLM-specific params
    best_of: int | None = None
    max_tokens: int | None = None
    frequency_penalty: float | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
