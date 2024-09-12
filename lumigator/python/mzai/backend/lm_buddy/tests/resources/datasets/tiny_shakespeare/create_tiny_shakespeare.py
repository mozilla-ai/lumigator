"""Script to generate the `tiny_shakespeare` dataset files."""
from pathlib import Path

from datasets import load_dataset

if __name__ == "__main__":
    repo_id = "Trelis/tiny-shakespeare"
    dataset = load_dataset(repo_id, split="train[:10]")
    dataset = dataset.rename_column("Text", "text")
    dataset.save_to_disk(dataset_path=Path(__file__).parent)
