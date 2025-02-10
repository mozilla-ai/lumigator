# Bring Your Own Local LLMs
Previously we saw how to use Lumigator with models on Hugging Face as well as via APIs hosted by [Open AI and Mistral](../user-guides/inference.md#model-specification). However, sometimes it may be advantageous to run models locally as a more cost-effective solution or when dealing with sensitive data or during the early stages of experimentation.

Lumigator supports running inference and evaluation on any locally hosted models through [Llamafile](https://github.com/Mozilla-Ocho/llamafile), [Ollama](https://ollama.com/search) and [vLLM](https://docs.vllm.ai/en/latest/), thanks to their compatibility with [OpenAI's Completions API Client](https://github.com/openai/openai-python). This guide will walk you through the process of running evaluation on any local model that you bring from these providers (assuming your machine meets the necessary hardware requirements).

Before installation and setup, here are some recommended system requirements:
* Memory (RAM): 8GB minimum, 16GB or more recommended
* Storage: At least 10GB or more of free space
* Processor: A relatively modern CPU with atleast 4 cores

## What You’ll Need
1. A running instance of [Lumigator](../get-started/installation.md).
    ```{note}
    **Before to starting up** the Lumigator application, you need to set a value for the `OPENAI_API_KEY` environment variable. This is because all the local model inference tools discussed here are based on OpenAI API compatible client. However, since we are going to run the models locally, this variable can be set to any placeholder value.
    ```console
    user@host:~/lumigator$ export OPENAI_API_KEY="abc123" # pragma: allowlist secret
    ```

2. A dataset for experimentation: You can use the {{ '[sample dataset](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }} provided in the [Lumigator repository](https://github.com/mozilla-ai/lumigator) or upload your own dataset through the [Lumigator UI](../get-started/ui-guide.md#upload-a-dataset).


3. Create a bash file `common_variables.sh` and initialize the following variables before proceeding with different local LLM tools.
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

You have a choice of choosing one among the below-mentioned local LLM tools. We describe the steps to locally stand up your desired model and enable Lumigator to query the local model's inference endpoint.

## Llamafile
[Llamafile](https://github.com/Mozilla-Ocho/llamafile) bundles LLM weights and a specially-compiled version of [llama.cpp](https://github.com/ggerganov/llama.cpp) into a single executable file, allowing users to run large language models locally without any additional setup or dependencies.

### Procedure
#### 1. Download and Setup Llamafile Locally
   * Download any model's Llamafile from the official [repo](https://github.com/Mozilla-Ocho/llamafile?tab=readme-ov-file#other-example-llamafiles). For example, `mistral-7b-instruct-v0.2.Q4_0.llamafile` is a 3.85 GB Llamafile to get started with (alternatively `Llama-3.2-1B-Instruct.Q6_K.llamafile` is smaller at 1.11 GB).
   * Grant execution permissions: `chmod +x mistral-7b-instruct-v0.2.Q4_0.llamafile`.
   * Start the application locally with `./mistral-7b-instruct-v0.2.Q4_0.llamafile`.

#### 2. Verify Llamafile is Running
You should be able to see it running on [localhost:8080](http://localhost:8080/). Note that this is the endpoint that Lumigator will use to interact with.

#### 3. Run Lumigator Evaluation
Create a new bash script `test_local_llm_eval.sh`:
```bash
#!/bin/bash
source common_variables.sh

EVAL_NAME="Llamafile mistral-7b-instruct-v0.2"
EVAL_DESC="Test evaluation with mistral-7b-instruct-v0.2"
EVAL_MODEL="llamafile://mistral-7b-instruct-v0.2" # Format llamafile://<model_name>
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
```console
user@host:~/lumigator$ bash test_local_llm_eval.sh
```

You can view the results on the UI as described [below](./local-models.md#view-evaluation-results).

## Ollama
[Ollama](https://github.com/ollama/ollama) provides a simplified way to download, manage, and interact with various open-source LLMs either from the command line or with [web UI](https://docs.openwebui.com/).

### Procedure
#### 1. Setup Ollama Completions Endpoint Locally
* Download and install Ollama for your operating system from the [official website](https://ollama.com/download).
* Select a model from the [available list](https://ollama.com/search) that you would like to use for evaluation (e.g. `llama3.2`) and run:
  ```console
  user@host:~/lumigator$ ollama run llama3.2
  ```

#### 2. Verify Ollama is Running
A Ollama completions endpoint should start running locally and can be verified by visiting [localhost:11434](http://localhost:11434/).

#### 3. Run Lumigator Evaluation
The evaluation steps are similar to earlier but we modify model details in the  `test_local_llm_eval.sh` script:
```bash
#!/bin/bash
source common_variables.sh

EVAL_NAME="Ollama Llama3.2"
EVAL_DESC="Test evaluation with Ollama's Llama3.2"
EVAL_MODEL="ollama://llama3.2" # Format expected ollama://<model_name>, the model_name must be same as one used in the `ollama run <model_name>` command
EVAL_MODEL_URL="http://localhost:11434/v1" # Ollama runs on port 11434

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

Run the evaluation:
```console
user@host:~/lumigator$ bash test_local_llm_eval.sh
```

Finally, view the results on the UI as described [below](./local-models.md#view-evaluation-results).


## vLLM
[vLLM](https://github.com/vllm-project/vllm) is a high-performance library for LLM inference and serving, featuring optimized memory management techniques. Apart from cloud deployments, it also comes with options to deploy models locally. Moreover, with vLLM you can host any model available on the [HuggingFace Model Hub](https://huggingface.co/models).
As a pre-requisite, you will need to create an account on HuggingFace and [setup an API token](https://huggingface.co/settings/tokens).
```console
user@host:~/$ export HUGGING_FACE_HUB_TOKEN=<your_huggingface_token>
```

### Procedure
#### 1. Setup vLLM Completions Endpoint Locally
* While vLLM provides an [official Docker image](https://docs.vllm.ai/en/latest/deployment/docker.html#use-vllm-s-official-docker-image), it assumes that you have GPUs available. However, if you are running vLLM on a machine without GPUs, you can use the [Dockerfile.cpu](https://github.com/vllm-project/vllm/blob/main/Dockerfile.cpu) for x86 architecture and [Dockerfile.arm](https://github.com/vllm-project/vllm/blob/main/Dockerfile.arm) for ARM architecture.
  ```console
  user@host:~/$ git clone https://github.com/vllm-project/vllm.git
  user@host:~/$ cd vllm
  user@host:~/vllm$ build -f Dockerfile.arm -t vllm-cpu --shm-size=6g .
  user@host:~/vllm$ docker run -it --rm -p 8090:8000 \
                    --env "HUGGING_FACE_HUB_TOKEN=$HUGGING_FACE_HUB_TOKEN" \
                    vllm-cpu --model HuggingFaceTB/SmolLM2-360M-Instruct \
                    --dtype float16
  ```
  ```{note}
  We are using the [SmolLM2-360M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) model here but you can specify any other model from the [Hugging Face Hub](https://huggingface.co/models) that runs on your hardware. We allocate 6 GB of memory for the docker container so that the model fits in memory and use port 8090 for the vLLM server (since the vLLM default port 8000 is already being used by Lumigator).
  ```

#### 2. Verify vLLM is Running
If successful, you should see the vLLM server running on [localhost:8090/docs](http://localhost:8090/docs) and your chosen model listed on [localhost:8090/v1/models](http://localhost:8090/v1/models).


#### 3. Run Lumigator Evaluation
And make the necessary changes to your evaluation script to point to the local vLLM server and use the correct model:
```bash
#!/bin/bash
source common_variables.sh

EVAL_NAME="vLLM HuggingFaceTB/SmolLM2-360M-Instruct"
EVAL_DESC="Test evaluation with vLLM's HuggingFaceTB/SmolLM2-360M-Instruct"
EVAL_MODEL="vllm://HuggingFaceTB/SmolLM2-360M-Instruct" # Format expected vllm://<model_name>, the model_name must be same as one when running the docker container
EVAL_MODEL_URL="http://localhost:8090/v1" # vLLM setup to run on port 8090

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

Run the evaluation:
```console
user@host:~/lumigator$ bash test_local_llm_eval.sh
```

## View Evaluation Results
To view the evalution results, go to the [Lumigator UI](http://localhost) and navigate to the "Experiments" tab. Then, select the most recent experiment with your local LLM and click "View Results".

---
With that, you are equipped to run Lumigator evaluation on your dataset, with a local LLM of your choice.
