from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

PROMPT_FORMAT_CONFIGS = {
    "meta-llama/Meta-Llama-3-8B": {
        "system": "<|start_header_id|>system<|end_header_id|>\n\n{instruction}<|eot_id|>",
        "assistant": "<|start_header_id|>assistant<|end_header_id|>\n\n{instruction}<|eot_id|>",
        "trailing_assistant": "",
        "user": "<|start_header_id|>user<|end_header_id|>\n\n{instruction}<|eot_id|>",
        "system_in_user": False,
        "bos": "<|begin_of_text|>",
        "default_system_message": "",
    },
}


class ModelTypeEnum(str, Enum):
    SW_RANKER = "sw_ranker"
    MATRIX_FACTORIZATION = "matrix_factorization"
    BERT = "bert"
    CAUSAL = "causal-llm"


class CausalRouterType(BaseModel):
    router_type: Literal[ModelTypeEnum.CAUSAL] = ModelTypeEnum.CAUSAL
    router_model_id: str
    model_id: str = "meta-llama/Meta-Llama-3-8B"
    model_config = ConfigDict(extra="forbid")


class BertRouterType(BaseModel):
    router_type: Literal[ModelTypeEnum.BERT] = ModelTypeEnum.BERT
    model_id: str
    model_config = ConfigDict(extra="forbid")


class SwRankerRouterType(BaseModel):
    router_type: Literal[ModelTypeEnum.SW_RANKER] = ModelTypeEnum.SW_RANKER
    model_config = ConfigDict(extra="forbid")


class MatrixFactorizationRouterType(BaseModel):
    router_type: Literal[ModelTypeEnum.MATRIX_FACTORIZATION] = ModelTypeEnum.MATRIX_FACTORIZATION
    model_config = ConfigDict(extra="forbid")


RouterDefinition = Annotated[
    CausalRouterType | BertRouterType | SwRankerRouterType | MatrixFactorizationRouterType,
    Field(discriminator="router_type"),
]


class ModelPair(BaseModel):
    pro: str
    lite: str


class RouterModelConfigRequest(BaseModel):
    router_definition: RouterDefinition
    model_pair: ModelPair
    num_outputs: int = 5
    threshold: float = 0.5
    score_threshold: int = 4
    special_tokens: tuple = ("[[1]]", "[[2]]", "[[3]]", "[[4]]", "[[5]]")
    flash_attention_2: bool = False
    attention_dropout: float = 0.0

    prompt: str
    prompt_format: dict = PROMPT_FORMAT_CONFIGS["meta-llama/Meta-Llama-3-8B"]

    model_config = ConfigDict(protected_namespaces=())


class RouterModelRequest(BaseModel):
    prompt: str
    prompt_format: dict = PROMPT_FORMAT_CONFIGS["meta-llama/Meta-Llama-3-8B"]


class RouterModelResponse(BaseModel):
    model_id: str
