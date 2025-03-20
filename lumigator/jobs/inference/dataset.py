from datasets import Dataset
from inference_config import InferenceJobConfig
from model_clients.huggingface_clients import is_encoder_decoder
from torch.utils.data import DataLoader
from torch.utils.data import Dataset as TorchDataset

from schemas import TaskType


def create_dataloader(dataset: Dataset, config: InferenceJobConfig):
    batch_size = config.job.batch_size
    use_chat_format_dataset = False

    if (
        config.inference_server
        or config.hf_pipeline.task == TaskType.TEXT_GENERATION
        # If the task is translation or summarization and the model is not an encoder-decoder model
        or (
            config.hf_pipeline.task in [TaskType.TRANSLATION, TaskType.SUMMARIZATION]
            and not is_encoder_decoder(config.hf_pipeline.model_name_or_path)
        )
    ):
        use_chat_format_dataset = True

    if use_chat_format_dataset:
        torch_dataset = ChatFormatDataset(dataset, config)
        return DataLoader(
            torch_dataset, batch_size=batch_size, shuffle=False, collate_fn=lambda batch: {"examples": batch}
        )
    else:
        torch_dataset = dataset.with_format("torch")
        return DataLoader(torch_dataset, batch_size, shuffle=False)


class ChatFormatDataset(TorchDataset):
    def __init__(self, dataset: Dataset, config: InferenceJobConfig):
        """Convert Hugging Face dataset to PyTorch Dataset with chat format.

        Args:
            dataset (datasets.Dataset): Input Hugging Face dataset
        """
        self.examples = dataset["examples"]
        self.system_prompt = config.system_prompt

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
