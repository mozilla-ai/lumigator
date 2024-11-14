# Inference

Inference jobs run predictive processes for (large) language models, on a Ray cluster.

The package currently exposes an inference job using a few model clients, for Hugging Face models,
OpenAI API compatible models, and Mistral models. The job is intended to be run on a Ray cluster,
and is submitted via the Lumigator API.
