import pytest
from datasets import load_from_disk

from lm_buddy.preprocessing import format_dataset_with_prompt


def test_prompt_formatting(resources_dir):
    dataset = load_from_disk(str(resources_dir / "datasets" / "tiny_shakespeare"))

    template = "Let's put some {text} in here"
    formatted_dataset = format_dataset_with_prompt(dataset, template, output_field="prompt")
    assert "prompt" in formatted_dataset.column_names

    bad_template = "A template that {requires} something extra."
    with pytest.raises(ValueError):
        format_dataset_with_prompt(dataset, bad_template, output_field="prompt")
