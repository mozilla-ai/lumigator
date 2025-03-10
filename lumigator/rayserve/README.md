# vLLM Ray Serve Deployment

This repository provides a [Ray Serve](https://docs.ray.io/en/latest/serve/index.html) deployment for running any
[vLLM](https://docs.vllm.ai/en/latest/)-supported model on a Kubernetes cluster. The deployment is built using FastAPI
and exposes an OpenAI-compatible API for inference.

## Prerequisites

  - Kubernetes cluster with [KubeRay](https://github.com/ray-project/kuberay) installed.
  - GPU-enabled nodes for efficient inference.

## Features

  - Supports any vLLM-compatible model.
  - OpenAI API-compatible `/v1/chat/completions`` endpoint.
  - LoRA modules and prompt adapters support.
  - Optimized for Kubernetes deployment with Ray Serve.

## Environment Variables

The script expects the following environment variables:

| Variable                      | Description                                                                         |
|-------------------------------|-------------------------------------------------------------------------------------|
| `MODEL_ID`                    | The identifier for the model to be deployed (e.g., `deepseek-ai/DeepSeek-V3`).      |
| `SERVED_MODEL_NAME`           | The name under which the model will be served.                                      |
| `TENSOR_PARALLELISM`          | Number of tensor parallelism partitions for model inference (i.e., number of GPUs). |
| `PIPELINE_PARALLELISM`        | Number of pipeline parallelism stages (i.e., number of nodes).                      |
| `DTYPE`                       | Weights data type (e.g., `float16`, `bfloat16`, etc.).                              |
| `GPU_MEMORY_UTILIZATION`      | Fraction of GPU memory to be used for the model (e.g., `"0.8"` for 80%).            |
| `DISTRIBUTED_EXECUTOR_BACKEND`| The backend used for distributed execution (`ray` or `mp`).                         |
| `TRUST_REMOTE_CODE`           | Whether to allow loading external model code (`"true"` or `"false"`).               |
