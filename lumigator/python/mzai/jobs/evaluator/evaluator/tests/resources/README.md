# Test resources

Static resources for LM Buddy testing.

These resources are manually created by developers and comitted to the repo
so that they can be loaded during tests without making network calls.
Test resources should be kept as small as possible to minimize the git repo size.
Currently, this includes the sub-folders:

- `datasets`: HuggingFace datasets
- `models`: HuggingFace model and tokenizers

## Generating new resources

When possible, the script for creating a resource should be included in the committed files.
See the current scripts in the `datasets` or `models` folders for an example.
