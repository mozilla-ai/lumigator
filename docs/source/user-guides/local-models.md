# Bring Your Own Local LLMs

Previously we saw how to use Lumigator with models on Hugging Face as well as via APIs hosted by [Open AI and Mistral](../user-guides/inference.md#model-specification). However, sometimes it may be advantageous to run models on-premise as a more cost-effective solution or when dealing with sensitive data or during the early stages of experimentation.

Lumigator supports running inference on any locally hosted models through [Llamafile](https://github.com/Mozilla-Ocho/llamafile), [Ollama](https://ollama.com/search) and [vLLM](https://docs.vllm.ai/en/latest/), thanks to their compatibility with [OpenAI's Completions API Client](https://github.com/openai/openai-python). This guide will walk you through the process of running inference (i.e. get predictions made by the model you are running locally) on any local model that you bring from these providers (assuming your machine meets the necessary hardware requirements).

Before installation and setup, here are some recommended system requirements:
* Memory (RAM): 8GB minimum, 16GB or more recommended
* Storage: At least 10GB or more of free space
* Processor: A relatively modern CPU with at least 4 cores

This tutorial will show you how to perform inference as a single job. If you would like to do this as a part of an experiment and workflow (which includes evaluation of the results), see [the quickstart](../get-started/quickstart.md#using-lumigator).

## What You’ll Need

1. A running instance of [Lumigator](../get-started/quickstart.md).

2. A dataset for experimentation: you can upload the {{ '[sample dataset](https://github.com/mozilla-ai/lumigator/blob/{}/lumigator/sample_data/dialogsum_exc.csv)'.format(commit_id) }} provided in the [Lumigator repository](https://github.com/mozilla-ai/lumigator) or upload your own dataset through the [Lumigator UI](../get-started/ui-guide.md#upload-a-dataset).

3. Create a bash file `common_variables.sh` and initialize the following variables before proceeding with different local LLM tools.
    ```bash
    #!/bin/bash
    BACKEND_URL=http://localhost:8000 # Lumigator runs on port 8000

    # Get the most recently uploaded dataset
    INFERENCE_DATASET_ID=$(curl -s "$BACKEND_URL/api/v1/datasets/" | grep -o '"id":"[^"]*"' | head -n1 | cut -d'"' -f4)

    # Basic prompt for LLM, summarization task
    INFERENCE_SYSTEM_PROMPT="You are a helpful assistant, expert in text summarization. For every prompt you receive, provide a summary of its contents in at most two sentences."

    # Run inference on first 10 rows in the csv, set to -1 if you would like to run it for all rows
    INFERENCE_MAX_SAMPLES="10"
    ```

You have a choice of choosing one among the below-mentioned local LLM tools. We describe the steps to locally stand up your desired model and enable Lumigator to query the local model's inference endpoint.

## Llamafile
[Llamafile](https://github.com/Mozilla-Ocho/llamafile) bundles LLM weights and a specially-compiled version of [llama.cpp](https://github.com/ggerganov/llama.cpp) into a single executable file, allowing users to run large language models locally without any additional setup or dependencies.

### Procedure

1. Download and setup Llamafile locally following the instructions from the [official repo](https://github.com/Mozilla-Ocho/llamafile?tab=readme-ov-file#quickstart).
   For example, you could use `mistral-7b-instruct-v0.2.Q4_0.llamafile` which is a 3.85 GB Llamafile to get started (or alternatively `Llama-3.2-1B-Instruct.Q6_K.llamafile` which is only 1.11 GB).

1. Verify Llamafile is Running. You should be able to see it running on
   [localhost:8080](http://localhost:8080/). Note that this is the endpoint that Lumigator will use
   to interact with.

1. Run Lumigator Inference. Create a new bash script `test_local_llm_inference.sh`:

   ```bash
   #!/bin/bash
   source common_variables.sh

   INFERENCE_NAME="Llamafile mistral-7b-instruct-v0.2"
   INFERENCE_DESC="Test inference with mistral-7b-instruct-v0.2"
   INFERENCE_MODEL="mistralai/mistral-7b-instruct-v0.2" # The model we are using
   INFERENCE_PROVIDER="openai" # The protocol/provider to use, which is the OpenAI API
   INFERENCE_BASE_URL="http://localhost:8080/v1" # Llamafile runs on port 8080 so we will make our OpenAI calls to this endpoint

   curl -s "$BACKEND_URL/api/v1/jobs/inference/" \
   -H 'Accept: application/json' \
   -H 'Content-Type: application/json' \
   -d '{
      "name": "'"$INFERENCE_NAME"'",
      "description": "'"$INFERENCE_DESC"'",
      "dataset": "'"$INFERENCE_DATASET_ID"'",
      "max_samples": "'"$INFERENCE_MAX_SAMPLES"'",
      "job_config": {
         "job_type": "'"inference"'",
         "model": "'"$INFERENCE_MODEL"'",
         "provider": "'"$INFERENCE_PROVIDER"'",
         "base_url": "'"$INFERENCE_BASE_URL"'",
         "system_prompt": "'"$INFERENCE_SYSTEM_PROMPT"'"
      }
   }'
   ```

   Finally execute the bash script:
   ```console
   user@host:~/lumigator$ bash test_local_llm_inference.sh
   ```

You can then download the results following the steps described [below](#download-inference-results)

## Ollama
[Ollama](https://github.com/ollama/ollama) provides a simplified way to download, manage, and interact with various open-source LLMs either from the command line or with [web UI](https://docs.openwebui.com/).

### Procedure

1. Setup Ollama Completions Endpoint Locally

   * Download and install Ollama for your operating system from the [official website](https://ollama.com/download).
   * Select a model from the [available list](https://ollama.com/search) that you would like to use for inference (e.g. `llama3.2`) and run:
      ```console
      user@host:~/lumigator$ ollama run llama3.2
      ```

1. Verify Ollama is Running. An Ollama completions endpoint should start running locally and can be
   verified by visiting [localhost:11434](http://localhost:11434/).

1. Run Lumigator Inference. The inference steps are similar to earlier but we modify model details
   in the  `test_local_llm_inference.sh` script:

   ```bash
   #!/bin/bash
   source common_variables.sh

   INFERENCE_NAME="Ollama Llama3.2"
   INFERENCE_DESC="Test inference with Ollama's Llama3.2"
   INFERENCE_MODEL="llama3.2" # Format expected ollama://<model_name>, the model_name must be same as one used in the `ollama run <model_name>` command
   INFERENCE_PROVIDER="openai" # The protocol/provider to use, which is the OpenAI API
   INFERENCE_BASE_URL="http://localhost:11434/v1" # Ollama runs on port 11434

   curl -s "$BACKEND_URL/api/v1/jobs/inference/" \
   -H 'Accept: application/json' \
   -H 'Content-Type: application/json' \
   -d '{
      "name": "'"$INFERENCE_NAME"'",
      "description": "'"$INFERENCE_DESC"'",
      "dataset": "'"$INFERENCE_DATASET_ID"'",
      "max_samples": "'"$INFERENCE_MAX_SAMPLES"'",
      "job_config": {
         "job_type": "'"inference"'",
         "model": "'"$INFERENCE_MODEL"'",
         "provider": "'"$INFERENCE_PROVIDER"'",
         "base_url": "'"$INFERENCE_BASE_URL"'",
         "system_prompt": "'"$INFERENCE_SYSTEM_PROMPT"'"
      }
   }'
   ```

   Finally execute the bash script:
   ```console
   user@host:~/lumigator$ bash test_local_llm_inference.sh
   ```

Finally, download the results as described [below](#download-inference-results)

## vLLM

[vLLM](https://github.com/vllm-project/vllm) is a high-performance library for LLM inference and serving, featuring optimized memory management techniques. Apart from cloud deployments, it also comes with options to deploy models locally. Moreover, with vLLM you can host any model available on the [HuggingFace Model Hub](https://huggingface.co/models).

As a pre-requisite, you will need to create an account on HuggingFace and [setup an API token](https://huggingface.co/settings/tokens).

```console
user@host:~/$ export HUGGING_FACE_HUB_TOKEN=<your_huggingface_token>
```

### Procedure

1. Setup vLLM Completions Endpoint Locally. While vLLM provides an [official Docker image](https://docs.vllm.ai/en/latest/deployment/docker.html#use-vllm-s-official-docker-image), it assumes that you have GPUs available. However, if you are running vLLM on a machine without GPUs, you can use the [Dockerfile.cpu](https://github.com/vllm-project/vllm/blob/main/Dockerfile.cpu) for x86 architecture and [Dockerfile.arm](https://github.com/vllm-project/vllm/blob/main/Dockerfile.arm) for ARM architecture.

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
   We are using the [SmolLM2-360M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) model here but you can specify any other model from the [Hugging Face Hub](https://huggingface.co/models) that runs on your hardware, but please note that requirements may vary significantly for different models. For specific setup instructions, please refer to the vLLM and Hugging Face documentation. We allocate 6 GB of memory for the docker container so that the model fits in memory and use port 8090 for the vLLM server (since the vLLM default port 8000 is already being used by Lumigator).
   ```

1. Verify vLLM is Running. If successful, you should see the vLLM server running on [localhost:8090/docs](http://localhost:8090/docs) and your chosen model listed on [localhost:8090/v1/models](http://localhost:8090/v1/models).


1. Run Lumigator Inference. Make the necessary changes to your inference script to point to the local vLLM server and use the correct model:

   ```bash
   #!/bin/bash
   source common_variables.sh

   INFERENCE_NAME="vLLM HuggingFaceTB/SmolLM2-360M-Instruct"
   INFERENCE_DESC="Test inference with vLLM's HuggingFaceTB/SmolLM2-360M-Instruct"
   INFERENCE_MODEL="HuggingFaceTB/SmolLM2-360M-Instruct" # Format expected vllm://<model_name>, the model_name must be same as one when running the docker container
   INFERENCE_PROVIDER="hosted_vllm" # Provider as documented in LiteLLM https://docs.litellm.ai/docs/providers/vllm
   INFERENCE_BASE_URL="http://localhost:8090/v1" # vLLM setup to run on port 8090

   curl -s "$BACKEND_URL/api/v1/jobs/inference/" \
   -H 'Accept: application/json' \
   -H 'Content-Type: application/json' \
   -d '{
      "name": "'"$INFERENCE_NAME"'",
      "description": "'"$INFERENCE_DESC"'",
      "dataset": "'"$INFERENCE_DATASET_ID"'",
      "max_samples": "'"$INFERENCE_MAX_SAMPLES"'",
      "job_config": {
         "job_type": "'"inference"'",
         "model": "'"$INFERENCE_MODEL"'",
         "provider": "'"$INFERENCE_PROVIDER"'",
         "base_url": "'"$INFERENCE_BASE_URL"'",
         "system_prompt": "'"$INFERENCE_SYSTEM_PROMPT"'"
      }
   }'
   ```

   Finally execute the bash script:
   ```console
   user@host:~/lumigator$ bash test_local_llm_inference.sh
   ```

To download the inference results, refer to the section [below](#download-inference-results)

## Download Inference Results
You can download and view the results of the inference job with the following script `download_local_llm_results.sh`:
```bash
#!/bin/bash

source common_variables.sh

JOB_ID=e36d91cb-d642-4d70-9ae2-dcc94a745fb4 #$(curl -s "$BACKEND_URL/api/v1/jobs/" | grep -o '"id":"[^"]*"' | head -n1 | cut -d'"' -f4)

echo "Looking for $JOB_ID results..."
DOWNLOAD_RESPONSE=$(curl -s $BACKEND_URL/api/v1/jobs/$JOB_ID/result/download)
DOWNLOAD_URL=$(echo $DOWNLOAD_RESPONSE | grep -o '"download_url":"[^"]*"' | sed 's/"download_url":"//;s/"//')
RESULTS_FILE=${JOB_ID}_results.json
echo "Downloading from $DOWNLOAD_URL..."
   curl $DOWNLOAD_URL -o $RESULTS_FILE

cat $RESULTS_FILE | python -m json.tool
```

And the last step is to execute the script:
```console
user@host:~/lumigator$ bash download_local_llm_results.sh
```

## Conclusion

Congratulations. You are now ready to run Lumigator inference on any local LLM of your choice!
