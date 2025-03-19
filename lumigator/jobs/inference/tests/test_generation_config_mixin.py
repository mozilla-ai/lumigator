import pytest
from inference_config import GenerationConfig
from model_clients.mixins.generation_config_mixin import GenerationConfigMixin


@pytest.mark.parametrize(
    "config, max_pos_emb, expected_max_new_tokens, expected_log",
    [
        (
            GenerationConfig(max_new_tokens=0),
            512,
            512,
            "Setting max_length to the max supported length by the model: 512",
        ),
        (GenerationConfig(max_new_tokens=256), 512, 256, "Setting max_length to 256"),
        (
            GenerationConfig(max_new_tokens=1024),
            512,
            512,
            "Requested 1024 tokens, but model supports only 512. Setting max_length to 512",
        ),
    ],
)
def test_adjust_config_max_new_tokens(config, max_pos_emb, expected_max_new_tokens, expected_log, caplog_with_loguru):
    mixin = GenerationConfigMixin()
    updated_config = mixin.adjust_config_max_new_tokens(config, max_pos_emb)

    assert updated_config.max_new_tokens == expected_max_new_tokens
    assert expected_log in caplog_with_loguru.text


def test_adjust_config_max_new_tokens_raises_type_error():
    mixin = GenerationConfigMixin()
    with pytest.raises(TypeError, match="The config cannot be None"):
        mixin.adjust_config_max_new_tokens(None, 512)
