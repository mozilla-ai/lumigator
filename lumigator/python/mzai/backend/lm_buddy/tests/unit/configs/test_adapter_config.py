import pytest
from peft import PeftType, TaskType
from pydantic import ValidationError

from lm_buddy.configs.huggingface import AdapterConfig


def test_enum_sanitzation():
    config = AdapterConfig(peft_type="lora  ", task_type="  causal_lm")
    assert config.peft_type == PeftType.LORA
    assert config.task_type == TaskType.CAUSAL_LM


def test_extra_field_validation():
    for peft_type in PeftType:
        with pytest.raises(ValidationError):
            AdapterConfig(
                peft_type=peft_type,
                task_type=TaskType.CAUSAL_LM,
                extra_bad_field_name="123",
            )


def test_huggingface_conversion():
    for peft_type in PeftType:
        config = AdapterConfig(peft_type=peft_type)

        hf_config = config.as_huggingface()
        expected_cls = AdapterConfig._get_peft_config_class(peft_type)
        assert type(hf_config) is expected_cls
