import string
from typing import Any

from datasets import Dataset


def format_dataset_with_prompt(
    dataset: Dataset,
    prompt_template: str,
    output_field: str,
    *,
    num_proc: int = 1,
) -> Dataset:
    fields = _get_template_fields(prompt_template)

    missing_columns = fields.difference(dataset.column_names)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing columns for the following prompt fields: {missing_columns}"
        )

    # Formatter is typed for single examples
    def formatting_func(examples: dict[str, Any]):
        format_data = {k: examples[k] for k in fields}
        examples[output_field] = prompt_template.format(**format_data)
        return examples

    return dataset.map(formatting_func, num_proc=num_proc, batched=False)


def _get_template_fields(template: str) -> set[str]:
    """Returns the fields in the template."""
    parsed = [x for x in string.Formatter().parse(template) if x[1] is not None]
    fields = {field for _, field, _, _ in parsed}
    return fields
