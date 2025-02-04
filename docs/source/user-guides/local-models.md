# Bring Your Own Local LLMs
Previously we saw how to use Lumigator with models on Hugging Face as well as via APIs hosted by [Open AI and Mistral](../user-guides/inference.md#model-specification). However, sometimes it may be advantageous to run models locally as a more cost-effective solution or when dealing with sensitive data or during the early stages of experimentation. Lumigator supports running inference and evaluation on locally models hosted through [Llamafile](https://github.com/Mozilla-Ocho/llamafile), [Ollama](https://ollama.com/search) and [vLLM](https://docs.vllm.ai/en/latest/), which enable locally hosting several LLMs. This guide will walk you through the process of running evalutation on any local model that you bring from these providers (assuming your machine meets the necessary hardware requirements).

## Getting Started
Assuming that you have already installed Lumigator and have the application [running](../get-started/installation.md#local-deployment), the first step is to upload a dataset. You can do this through the [Lumigator UI](../get-started/ui-guide.md), which can be accessed by visiting [localhost](http://localhost). You can get started by uploading the {{ '[sample dataset](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }} provided in the [Lumigator repository](https://github.com/mozilla-ai/lumigator).

Next, you have a choice between choosing one of the below-mentioned local LLM tools. Next, we describe the steps locally host your desired model and enable Lumigator to query the local model's inference endpoint.

## Llamafile


## Ollama


## vLLM
