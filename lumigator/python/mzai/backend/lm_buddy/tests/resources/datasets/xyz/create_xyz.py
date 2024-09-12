"""Script to generate the `xyz` dataset files."""
from pathlib import Path

from datasets import Dataset

if __name__ == "__main__":
    mappings = [{"x": i, "y": 2 * i, "z": 3 * i + 10} for i in range(100)]
    dataset = Dataset.from_list(mappings)
    dataset.save_to_disk(dataset_path=Path(__file__).parent)
