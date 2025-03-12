from datasets import Dataset
from inference_config import InferenceJobConfig
from torch.utils.data import DataLoader
from torch.utils.data import Dataset as TorchDataset

from schemas import TaskType


def create_dataloader(dataset: Dataset, config: InferenceJobConfig):
    batch_size = config.job.batch_size

    if (
        config.inference_server
        or config.hf_pipeline.task == TaskType.TEXT_GENERATION
        or config.hf_pipeline.task == TaskType.TRANSLATION
    ):
        torch_dataset = HuggingFaceDataset(dataset, config.system_prompt)
        return DataLoader(
            torch_dataset, batch_size=batch_size, shuffle=False, collate_fn=lambda batch: {"examples": batch}
        )
    else:
        torch_dataset = dataset.with_format("torch")
        return DataLoader(torch_dataset, batch_size, shuffle=False)


class HuggingFaceDataset(TorchDataset):
    def __init__(self, dataset: Dataset, system_prompt: str):
        """Convert Hugging Face dataset to PyTorch Datasets.

        Args:
            dataset (datasets.Dataset): Input Hugging Face dataset
        """
        self.examples = dataset["examples"]
        self.system_prompt = system_prompt

    def __len__(self):
        """Return the total number of examples."""
        return len(self.examples)

    def __getitem__(self, idx):
        """Retrieve a single sample and its ground truth

        Args:
            idx (int): Index of the sample

        Returns:
            list: OpenAI compatible request
        """
        return [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": self.examples[idx]}]
