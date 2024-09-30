import pytest
import torch
from tests.test_utils import copy_pydantic_json

from mzai.evaluator.configs.huggingface import QuantizationConfig


@pytest.fixture
def quantization_config() -> QuantizationConfig:
    return QuantizationConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
    )


def test_serde_round_trip(quantization_config: QuantizationConfig):
    assert copy_pydantic_json(quantization_config) == quantization_config
