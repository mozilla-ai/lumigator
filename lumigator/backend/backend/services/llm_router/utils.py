import torch
from lumigator_schemas.llm_router import PROMPT_FORMAT_CONFIGS, ModelTypeEnum, RouterModelConfigRequest
from transformers import AutoModelForCausalLM, AutoTokenizer

from backend.services.llm_router.prompt_formatter import PromptFormat
from backend.services.secrets import SecretService


def load_prompt_format(model_id):
    prompt_format_dict = PROMPT_FORMAT_CONFIGS[model_id]
    return PromptFormat(**prompt_format_dict, is_generation=True)


def to_openai_api_messages(system_message, classifier_message, messages):
    """Convert the conversation to OpenAI chat completion format."""
    ret = [{"role": "system", "content": system_message}]
    for i, turn in enumerate(messages):
        if i % 2 == 0:
            ret.append({"role": "user", "content": classifier_message.format(question=turn)})
        else:
            ret.append({"role": "assistant", "content": turn})
    return ret


def get_model(config: RouterModelConfigRequest, secret_service: SecretService = None, pad_token_id: int = 2):
    token = None
    if secret_service:
        token = secret_service.get_decrypted_secret_value("hf_token")

    if config.router_definition.router_type == ModelTypeEnum.CAUSAL:
        return AutoModelForCausalLM.from_pretrained(
            config.router_definition.router_model_id,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            use_cache=False,
            attn_implementation=("flash_attention_2" if config.flash_attention_2 else None),
            attention_dropout=config.attention_dropout,
            token=token,
        )
    else:
        raise NotImplementedError(f"ModelType {config.model_type} is not implemented yet!")


def get_tokenizer(config, secret_service=None, special_tokens=None, truncation_side="left", padding_side="left"):
    token = None
    if secret_service:
        token = secret_service.get_decrypted_secret_value("hf_token")

    # Context for legacy=True: https://github.com/huggingface/transformers/issues/25176
    tokenizer = AutoTokenizer.from_pretrained(
        config.router_definition.router_model_id,
        legacy=True,
        truncation_side=truncation_side,
        padding_side=padding_side,
        token=token,
    )
    tokenizer.pad_token = tokenizer.eos_token
    if special_tokens:
        tokenizer.add_tokens(special_tokens, special_tokens=True)
    return tokenizer
