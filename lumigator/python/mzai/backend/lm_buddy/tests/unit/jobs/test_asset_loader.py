import torch
from datasets import Dataset, DatasetDict

from lm_buddy.configs.huggingface import AutoModelConfig, DatasetConfig
from lm_buddy.jobs.asset_loader import HuggingFaceDatasetLoader, HuggingFaceModelLoader
from lm_buddy.paths import format_file_path


def test_dataset_loading(xyz_dataset_path):
    hf_loader = HuggingFaceDatasetLoader()

    asset_path = format_file_path(xyz_dataset_path)
    dataset_config = DatasetConfig(path=asset_path, test_size=0.2, seed=0)

    dataset = hf_loader.load_dataset(dataset_config)
    assert type(dataset) is Dataset

    datasets = hf_loader.load_and_split_dataset(dataset_config)
    assert type(datasets) is DatasetDict
    assert "train" in datasets and "test" in datasets


def test_model_loading(llm_model_path):
    hf_loader = HuggingFaceModelLoader()

    asset_path = format_file_path(llm_model_path)
    model_config = AutoModelConfig(path=asset_path, torch_dtype=torch.bfloat16)

    hf_config = hf_loader.load_pretrained_config(model_config)
    hf_model = hf_loader.load_pretrained_model(model_config)
    assert hf_config._name_or_path == hf_model.name_or_path
    assert hf_model.dtype == torch.bfloat16
