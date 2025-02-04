# Bring Your Own Local LLMs
Previously we saw how to use Lumigator with models on Hugging Face as well as via APIs hosted by [Open AI and Mistral](../user-guides/inference.md#model-specification). However, sometimes it may be advantageous to run models locally as a more cost-effective solution or when dealing with sensitive data or during the early stages of experimentation. Lumigator supports running inference and evaluation on any locally hosted models through [Llamafile](https://github.com/Mozilla-Ocho/llamafile), [Ollama](https://ollama.com/search) and [vLLM](https://docs.vllm.ai/en/latest/), thanks to their compatibility with [OpenAI's Completions API](https://platform.openai.com/docs/guides/completions). This guide will walk you through the process of running evaluation on any local model that you bring from these providers (assuming your machine meets the necessary hardware requirements).

## Getting Started
Assuming that you have already installed Lumigator and have the application [running](../get-started/installation.md#local-deployment), the first step is to upload a dataset. You can do this through the [Lumigator UI](../get-started/ui-guide.md), which can be accessed by visiting [localhost](http://localhost). You can get started by uploading the {{ '[sample dataset](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }} provided in the [Lumigator repository](https://github.com/mozilla-ai/lumigator).

Next, you have a choice between choosing one of the below-mentioned local LLM tools. Next, we describe the steps locally host your desired model and enable Lumigator to query the local model's inference endpoint.
Before installation, here are some recommended system requirements:
* Memory (RAM): 8GB minimum, 16GB or more recommended
* Storage: At least 10GB or more of free space
* Processor: A relatively modern CPU with atleast 4 cores

## Llamafile
[Llamafile](https://github.com/Mozilla-Ocho/llamafile) bundles LLM weights and a specially-compiled version of [llama.cpp](https://github.com/ggerganov/llama.cpp) into a single executable file, allowing users to run large language models locally without any additional setup or dependencies.

## Ollama
[Ollama](https://github.com/ollama/ollama) provides a simplified way to download, manage, and interact with various open-source LLMs either from the command line or with [web UI](https://docs.openwebui.com/).

## vLLM
[vLLM](https://github.com/vllm-project/vllm) is a high-performance library for LLM inference and serving, featuring optimized memory management techniques. Apart from cloud deployments, it also comes with options to deploy models locally.
