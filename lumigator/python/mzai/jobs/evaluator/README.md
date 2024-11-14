# Evaluator

The Evaluator spawns jobs to evaluate (large) language models, originating from
[lm-buddy](https://github.com/mozilla-ai/lm-buddy). It is used by Lumigator to initiate new
evaluation jobs on a Ray cluster.

Currently, the package supports evaluation jobs using HuggingFace's [evaluate](#), with inference
performed either via an in-process HuggingFace model, an externally-hosted vLLM server, OpenAI, Mistral.

Evaluator's commands are designed to be used as entry points for jobs on a Ray compute cluster. The
recommended method for submitting an evaluation job to Ray is by using the Lumigator Python SDK. For
more information, refer to the
[Lumigator documentation](https://mozilla-ai.github.io/lumigator/get-started/quickstart.html).
