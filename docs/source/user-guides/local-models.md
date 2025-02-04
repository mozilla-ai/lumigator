# Bring Your Own Local LLMs
Previously we saw how to use Lumigator with models on Hugging Face as well as via APIs hosted by [Open AI and Mistral](../user-guides/inference.md#model-specification). However, sometimes it may be advantageous to run models locally as a more cost-effective solution or when dealing with sensitive data or during the early stages of experimentation. Lumigator supports running inference and evaluation on any locally hosted models through [Llamafile](https://github.com/Mozilla-Ocho/llamafile), [Ollama](https://ollama.com/search) and [vLLM](https://docs.vllm.ai/en/latest/), thanks to their compatibility with [OpenAI's Completions API](https://platform.openai.com/docs/guides/completions). This guide will walk you through the process of running evaluation on any local model that you bring from these providers (assuming your machine meets the necessary hardware requirements).

Before installation and setup, here are some recommended system requirements:
* Memory (RAM): 8GB minimum, 16GB or more recommended
* Storage: At least 10GB or more of free space
* Processor: A relatively modern CPU with atleast 4 cores

## Getting Started
Assuming that you have already installed Lumigator and have the application [running](../get-started/installation.md#local-deployment), the first step is to upload a dataset. You can do this through the [Lumigator UI](../get-started/ui-guide.md), which can be accessed by visiting [localhost](http://localhost). You can get started by uploading the {{ '[sample dataset](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }} provided in the [Lumigator repository](https://github.com/mozilla-ai/lumigator).

Create a bash file `common_variables.sh` and initialize the following variables.

```bash
#!/bin/bash
BACKEND_URL=http://localhost:8000 # Lumigator runs on port 8000

# Get the most recently uploaded dataset
EVAL_DATASET_ID=$(curl -s "$BACKEND_URL/api/v1/datasets/" | grep -o '"id":"[^"]*"' | head -n1 | cut -d'"' -f4)

# Basic prompt for LLM, summarization task
EVAL_SYSTEM_PROMPT="You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."

# Run eval on first 10 rows in the csv, set to -1 if you would like to run it for all rows
EVAL_MAX_SAMPLES="10"
```

Next, you have a choice between choosing one of the below-mentioned local LLM tools. Next, we describe the steps locally host your desired model and enable Lumigator to query the local model's inference endpoint.

## Llamafile
[Llamafile](https://github.com/Mozilla-Ocho/llamafile) bundles LLM weights and a specially-compiled version of [llama.cpp](https://github.com/ggerganov/llama.cpp) into a single executable file, allowing users to run large language models locally without any additional setup or dependencies.

### Download and Run Llamafile Locally
1. Download any model's Llamafile from the official [repo](https://github.com/Mozilla-Ocho/llamafile?tab=readme-ov-file#other-example-llamafiles). For example, `mistral-7b-instruct-v0.2.Q4_0.llamafile` is a 3.85 GB Llamafile to get started with (alternatively `Llama-3.2-1B-Instruct.Q6_K.llamafile` is smaller at 1.11 GB).
2. Grant execution permissions: `chmod +x mistral-7b-instruct-v0.2.Q4_0.llamafile`
3. Start the application locally with `./mistral-7b-instruct-v0.2.Q4_0.llamafile`.

You should be able to see it running on http://localhost:8080/. Note that this is the endpoint that Lumigator will use to interact with.

### Run Lumigator Evaluation
Create a new bash script `test_local_llm_eval.sh`:
```bash
#!/bin/bash
source common_variables.sh

EVAL_NAME="Llamafile mistral-7b-instruct-v0.2"
EVAL_DESC="Test evaluation with mistral-7b-instruct-v0.2"
EVAL_MODEL="llamafile://mistral-7b-instruct-v0.2"
EVAL_MODEL_URL="http://localhost:8080/v1" # Llamafile runs on port 8080

# TODO: change to evaluate endpoint after experiments_new migration
curl -s "$BACKEND_URL/api/v1/jobs/inference/" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "'"$EVAL_NAME"'",
    "description": "'"$EVAL_DESC"'",
    "model": "'"$EVAL_MODEL"'",
    "dataset": "'"$EVAL_DATASET_ID"'",
    "max_samples": "'"$EVAL_MAX_SAMPLES"'",
    "model_url": "'"$EVAL_MODEL_URL"'",
    "system_prompt": "'"$EVAL_SYSTEM_PROMPT"'"
  }'

```

Finally run the evaluation:
``````console
user@host:~/lumigator$ test_local_llm_eval.sh
```

## Ollama
[Ollama](https://github.com/ollama/ollama) provides a simplified way to download, manage, and interact with various open-source LLMs either from the command line or with [web UI](https://docs.openwebui.com/).

### Run Ollama Completions Endpoint Locally

### Run Lumigator Evaluation

## vLLM
[vLLM](https://github.com/vllm-project/vllm) is a high-performance library for LLM inference and serving, featuring optimized memory management techniques. Apart from cloud deployments, it also comes with options to deploy models locally.

### Run vLLM Completions Endpoint Locally

### Run Lumigator Evaluation

## View Evaluation Results
To view the evalution results, go to the Lumigator UI and navigate to the "Experiments" tab. Then, select the most recent experiment with your local LLM and click "View Results".

---
With that, you are equipped to run Lumigator evaluation on your dataset, with a local LLM of your choice.
