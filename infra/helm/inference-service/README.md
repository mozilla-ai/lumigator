# Inference Service Helm Chart

This Helm chart is used for deploying models on Kubernetes using Ray and vLLM. Installing this chart will create a Ray
cluster and deploy a model serving application on top of it. The application will serve the model using the vLLM
library, and other libraries that are specified in the `runtimeEnv.pip` field.

## Installation

To install the Helm chart, you need to have the Helm CLI installed. You can install the Helm CLI by following the
instructions [here](https://helm.sh/docs/intro/install/). Once you have the Helm CLI installed, you can install the
chart by running the following command:

```bash
helm install <release-name> /path/to/inference-service-chart
```

You may also want to install the Helm chart from a Helm repository. To do this, you need to add the repository to your
Helm CLI:

```bash
helm repo add <repository-name> <repository-url>
helm repo update
```

Then, you can install the Helm chart from the repository:

```bash
helm install <release-name> <repository-name>/<chart-name>
```

## Configuration

The following table lists the configurable parameters of the `values.yaml` file and their default values.

### Inference Service Configuration

| Parameter                     | Description                                                                 | Default   |
|-------------------------------|-----------------------------------------------------------------------------|-----------|
| `inferenceServiceName`        | The name of the Ray Service to deploy. It should be 63 characters or less and must follow the DNS naming convention. | `""`      |
| `inferenceServiceNamespace`   | The namespace where the Ray Service will be deployed.                       | `default` |

### Application Configuration

| Parameter                               | Description                                                                 | Default   |
|-----------------------------------------|-----------------------------------------------------------------------------|-----------|
| `name`                      | The name of the application (e.g., deepseek-v3, llama-3, etc.).             | `""`      |
| `routePrefix`               | The route prefix used for serving the application (e.g., "/").              | `/`       |
| `importPath`                | The import path for the model to serve (e.g., lumigator.jobs.vllm.serve:model). | `lumigator.jobs.vllm.serve:model` |
| `numReplicas`               | The number of replicas for the deployment (e.g., 1).                        | `1`       |
| `numCpus`                   | Number of CPUs allocated for the Ray actor (e.g., 80).                      | `""`      |
| `workingDir`     | Working directory for the model (e.g., a zip file URL).                     | `""`      |
| `pip`            | List of Python packages to install in the runtime environment.              | `["vllm==0.7.2"]` |
| `modelID`| The path to the model. It can either be a model ID on Hugging Face Hub or a local path to the model directory. | `""`      |
| `servedModelName` | The name of the served model (e.g., DeepSeek-V3). This is an arbitrary name that you can use to identify the served model. | `""`      |
| `tensorParallelism` | Tensor parallelism level (e.g., 8) - number of GPUs per node.               | `""`      |
| `pipelineParallelism` | Pipeline parallelism level (e.g., 4) - number of nodes.                     | `""`      |
| `dType`  | Data type (e.g., "float32", "float16", "bfloat16", etc.).                   | `""`      |
| `gpuMemoryUtilization` | GPU memory utilization (e.g., 0.80). Controls how much of the GPU's total memory (VRAM) is allocated for the model's weights, activations, and key-value (KV) cache during inference. | `0.80`    |
| `distributedExecutorBackend` | Executor backend for distributed computing - 'ray' for Ray, 'mp' for multiprocessing. | `ray`     |
| `trustRemoteCode` | Whether or not to allow for custom code defined on the Hub in their own modeling, configuration, tokenization or even pipeline files. | `true`    |

### Ray Cluster Configuration

| Parameter                               | Description                                                                 | Default   |
|-----------------------------------------|-----------------------------------------------------------------------------|-----------|
| `image`                      | The Docker image to be used for both head and worker nodes (e.g., "rayproject/ray:2.41.0-py311-gpu"). | `rayproject/ray:2.41.0-py311-gpu` |
| `dashboardHost`              | The host for the Ray dashboard (e.g., "0.0.0.0").                           | `0.0.0.0` |
| `objectStoreMemory`          | Memory allocation for the object store (e.g., "1000000000" bytes). By default Ray allocates 30% of available memory to object storage, this leads to OOM issues for jobs. This parameter allows you to set the memory allocation for the object store to a fixed, lower value. | `1000000000` |
| `persistentVolumeClaimName`  | (Optional) Persistent volume claim name that stores the models (e.g., "models"). Leave it empty if you don't want to use a persistent volume claim. | `""`      |
| `headGroup.resources.limits.cpu` | CPU limit for the head node (e.g., "80").                                   | `""`      |
| `headGroup.resources.limits.memory` | Memory limit for the head node (e.g., "1000Gi").                            | `""`      |
| `headGroup.resources.limits.gpuCount` | (Optional) GPU limit for the head node (e.g., "8"). Leave it empty if you don't want to allocate GPUs to the head node. | `""`      |
| `headGroup.affinity.gpuClass` | (Optional) GPU class for node selection (e.g., "A100_NVLINK_80GB"). Leave it empty if you don't want to use GPU class for node selection. | `""`      |
| `headGroup.affinity.region`  | (Optional) Region for node selection (e.g., "US-EAST-04"). Leave it empty if you don't want to use region for node selection. | `""`      |
| `workerGroup.groupName`      | Name of the worker group (e.g., "worker-group").                            | `worker-group` |
| `workerGroup.replicas`       | Number of replicas for the worker group (e.g., "3").                        | `1`       |
| `workerGroup.resources.limits.cpu` | CPU limit for the worker nodes (e.g., "80").                                | `""`      |
| `workerGroup.resources.limits.memory` | Memory limit for the worker nodes (e.g., "1000Gi").                         | `""`      |
| `workerGroup.resources.limits.gpuCount` | (Optional) GPU limit for the worker nodes (e.g., "8"). Leave it empty if you don't want to allocate GPUs to the worker nodes. | `""`      |
| `workerGroup.affinity.gpuClass` | (Optional) GPU class for node selection (e.g., "A100_NVLINK_80GB"). Leave it empty if you don't want to use GPU class for node selection. | `""`      |
| `workerGroup.affinity.region` | (Optional) Region for node selection (e.g., "US-EAST-04"). Leave it empty if you don't want to use region for node selection. | `""`      |
