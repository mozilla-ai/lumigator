from unittest.mock import MagicMock, patch

import pytest
from inference_config import HfPipelineConfig
from model_clients.mixins.huggingface_pipeline_mixin import HuggingFacePipelineMixin
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Pipeline, PreTrainedTokenizer, pipeline

from schemas import TaskType


class MockHfPipelineConfig(HfPipelineConfig):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@pytest.fixture(scope="function")
def pipeline_config():
    mock_config = MagicMock(spec=HfPipelineConfig)
    mock_config.model_name_or_path = "hf-internal-testing/tiny-random-mt5"
    mock_config.trust_remote_code = False
    mock_config.torch_dtype = "auto"
    mock_config.use_fast = True
    mock_config.task = "translation"
    mock_config.revision = "main"
    mock_config.device = -1
    return mock_config


def test_initialize_model_none_config():
    mixin = HuggingFacePipelineMixin()
    with pytest.raises(TypeError, match="The pipeline_config cannot be None"):
        mixin.initialize_model(None)


@patch("model_clients.mixins.huggingface_pipeline_mixin.AutoModelForSeq2SeqLM")
def test_initialize_model_seq2seq(mock_automodel, pipeline_config):
    mock_model = MagicMock(spec=AutoModelForSeq2SeqLM)
    mock_automodel.from_pretrained.return_value = mock_model
    pipeline_config.task = TaskType.TRANSLATION
    mixin = HuggingFacePipelineMixin()
    model = mixin.initialize_model(pipeline_config)
    assert isinstance(model, AutoModelForSeq2SeqLM)
    mock_automodel.from_pretrained.assert_called_once_with(
        pipeline_config.model_name_or_path,
        trust_remote_code=pipeline_config.trust_remote_code,
        torch_dtype=pipeline_config.torch_dtype,
    )


def test_initialize_tokenizer_none_config():
    mixin = HuggingFacePipelineMixin()
    with pytest.raises(TypeError, match="The pipeline_config cannot be None"):
        mixin.initialize_tokenizer(None)


def test_initialize_pipeline(pipeline_config):
    mixin = HuggingFacePipelineMixin()
    model = mixin.initialize_model(pipeline_config)
    tokenizer = mixin.initialize_tokenizer(pipeline_config)
    pipeline_obj = mixin.initialize_pipeline(pipeline_config, model, tokenizer)
    assert isinstance(pipeline_obj, Pipeline)


@pytest.mark.parametrize(
    "model, tokenizer, pipeline_config, expected_exception, match",
    [
        (
            None,
            AutoTokenizer.from_pretrained("facebook/bart-large-cnn"),
            MockHfPipelineConfig(),
            TypeError,
            "The model cannot be None",
        ),
        (
            AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn"),
            None,
            MockHfPipelineConfig(),
            TypeError,
            "The tokenizer cannot be None",
        ),
        (
            AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn"),
            AutoTokenizer.from_pretrained("facebook/bart-large-cnn"),
            None,
            TypeError,
            "The pipeline_config cannot be None",
        ),
    ],
)
def test_initialize_pipeline_exceptions(model, tokenizer, pipeline_config, expected_exception, match):
    mixin = HuggingFacePipelineMixin()
    with pytest.raises(expected_exception, match=match):
        mixin.initialize_pipeline(pipeline_config, model, tokenizer)


def test_adjust_tokenizer_max_length(pipeline_config):
    mixin = HuggingFacePipelineMixin()
    mock_pipeline = MagicMock(spec=Pipeline)
    mock_pipeline.tokenizer = MagicMock(spec=PreTrainedTokenizer)
    mock_pipeline.tokenizer.model_max_length = 1024
    mixin.adjust_tokenizer_max_length(mock_pipeline, 512)
    assert mock_pipeline.tokenizer.model_max_length == 512


def test_adjust_tokenizer_max_length_no_change(pipeline_config):
    mixin = HuggingFacePipelineMixin()
    mock_pipeline = MagicMock(spec=Pipeline)
    mock_pipeline.tokenizer = MagicMock(spec=PreTrainedTokenizer)
    mock_pipeline.tokenizer.model_max_length = 512
    mixin.adjust_tokenizer_max_length(mock_pipeline, 512)
    assert mock_pipeline.tokenizer.model_max_length == 512


@pytest.mark.parametrize(
    "pipeline, max_pos_emb, expected_exception, match",
    [
        (None, 512, TypeError, "The pipeline cannot be None"),
        (MagicMock(spec=pipeline, tokenizer=None), 512, TypeError, "The pipeline's tokenizer cannot be None"),
    ],
)
def test_adjust_tokenizer_max_length_exceptions(pipeline, max_pos_emb, expected_exception, match):
    mixin = HuggingFacePipelineMixin()
    with pytest.raises(expected_exception, match=match):
        mixin.adjust_tokenizer_max_length(pipeline, max_pos_emb)
