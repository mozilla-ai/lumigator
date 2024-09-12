"""Script to generate the `tiny_gpt2` model and tokenizer files."""
import json
from pathlib import Path

from transformers import GPT2Config, GPT2Model, GPT2Tokenizer

BASE_PATH = Path(__file__).parent


def create_gpt2_tokenizer() -> GPT2Tokenizer:
    """Create a fake GPT2 tokenizer with a tiny vocab size.

    Source: https://github.com/huggingface/transformers/blob/main/tests/models/gpt2/test_tokenization_gpt2.py
    """
    vocab = [
        "l",
        "o",
        "w",
        "e",
        "r",
        "s",
        "t",
        "i",
        "d",
        "n",
        "\u0120",
        "\u0120l",
        "\u0120n",
        "\u0120lo",
        "\u0120low",
        "er",
        "\u0120lowest",
        "\u0120newer",
        "\u0120wider",
        "<unk>",
        "<|endoftext|>",
    ]
    vocab_tokens = dict(zip(vocab, range(len(vocab))))
    merges = ["#version: 0.2", "\u0120 l", "\u0120l o", "\u0120lo w", "e r", ""]
    special_tokens_map = {"unk_token": "<unk>"}

    vocab_file = BASE_PATH / "vocab.json"
    vocab_file.write_text(json.dumps(vocab_tokens) + "\n")

    merges_file = BASE_PATH / "merges.txt"
    merges_file.write_text("\n".join(merges))

    tokenizer = GPT2Tokenizer.from_pretrained(BASE_PATH, **special_tokens_map)
    return tokenizer


def create_gpt2_model(
    tokenizer: GPT2Tokenizer,
    *,
    n_head: int = 1,
    n_layer: int = 1,
    n_embd: int = 2,
) -> GPT2Model:
    config = GPT2Config(
        vocab_size=tokenizer.vocab_size,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.bos_token_id,
        n_head=n_head,
        n_layer=n_layer,
        n_embd=n_embd,
    )
    return GPT2Model(config)


if __name__ == "__main__":
    tokenizer = create_gpt2_tokenizer()
    model = create_gpt2_model(tokenizer)

    # Save model and tokenizer as resources
    model.save_pretrained(BASE_PATH)
    tokenizer.save_pretrained(BASE_PATH)
