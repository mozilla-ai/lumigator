# vLLM Ray Serve deployment

This guide provides step-by-step instructions to deploy a [vLLM](https://docs.vllm.ai/en/latest/)-supported model using
[Ray Serve](https://docs.ray.io/en/latest/serve/index.html) on a Kubernetes cluster. The deployment exposes an
OpenAI-compatible API for inference and supports advanced configurations like tensor parallelism, pipeline parallelism,
and LoRA modules.

## Prerequisites

- A Kubernetes cluster with [KubeRay](https://github.com/ray-project/kuberay) installed.
- GPU-enabled nodes for efficient inference.

## Procedure

1. Navigate to the `inference-service` Helm Chart, under the `infra` directory and configure your deployment, using the
   `values.yaml` file. Here's a list of the options:

   Ray Service configuration:

   | Parameter                   | Description                                              | Default   |
   |-----------------------------|----------------------------------------------------------|-----------|
   | `inferenceServiceName`      | Name of the Ray Service (max 63 chars, DNS-compliant).   | -         |
   | `inferenceServiceNamespace` | Namespace where the Ray Service is deployed.             | `default` |

   Application configuration:

   | Parameter                   | Description                                                 | Default                           |
   |-----------------------------|-------------------------------------------------------------|-----------------------------------|
   | `name`                      | Application name (e.g., deepseek-v3, llama-3).              | -                                 |
   | `routePrefix`               | Route prefix for serving (e.g., "/").                       | `/`                               |
   | `importPath`                | Import path for the model.                                  | `lumigator.jobs.vllm.serve:model` |
   | `numReplicas`               | Number of replicas.                                         | `1`                               |
   | `numCpus`                   | CPUs allocated per Ray actor.                               | -                                 |
   | `workingDir`                | Model working directory.                                    | -                                 |
   | `pip`                       | List of Python packages.                                    | `["vllm==0.7.2"]`                 |
   | `modelID`                   | Model path (Hugging Face ID or local directory).            | -                                 |
   | `servedModelName`           | Name of the served model.                                   | -                                 |
   | `tensorParallelism`         | Tensor parallelism (GPUs per node).                         | -                                 |
   | `pipelineParallelism`       | Pipeline parallelism (number of nodes).                     | -                                 |
   | `dType`                     | Data type (`float32`, `float16`, `bfloat16`, etc.).         | -                                 |
   | `gpuMemoryUtilization`      | Fraction of GPU memory allocated for inference.             | `0.80`                            |
   | `distributedExecutorBackend`| Executor backend (`ray` or `mp`).                           | `ray`                             |
   | `trustRemoteCode`           | Allow custom code from Hugging Face Hub.                    | `true`                            |

   Ray Cluster configuration:

   | Parameter                               | Description                                 | Default                           |
   |-----------------------------------------|---------------------------------------------|-----------------------------------|
   | `image`                                 | Docker image for Ray nodes.                 | `rayproject/ray:2.41.0-py311-gpu` |
   | `dashboardHost`                         | Ray dashboard host.                         | `0.0.0.0`                         |
   | `objectStoreMemory`                     | Object store memory allocation (bytes).     | `1000000000`                      |
   | `persistentVolumeClaimName`             | (Optional) PVC for model storage.           | -                                 |
   | `headGroup.resources.limits.cpu`        | Head node CPU limit.                        | -                                 |
   | `headGroup.resources.limits.memory`     | Head node memory limit.                     | -                                 |
   | `headGroup.resources.limits.gpuCount`   | (Optional) Head node GPU limit.             | -                                 |
   | `headGroup.affinity.gpuClass`           | (Optional) GPU class for head node.         | -                                 |
   | `headGroup.affinity.region`             | (Optional) Region for head node.            | -                                 |
   | `workerGroup.groupName`                 | Worker group name.                          | `worker-group`                    |
   | `workerGroup.replicas`                  | Number of worker group replicas.            | `1`                               |
   | `workerGroup.resources.limits.cpu`      | Worker node CPU limit.                      | -                                 |
   | `workerGroup.resources.limits.memory`   | Worker node memory limit.                   | -                                 |
   | `workerGroup.resources.limits.gpuCount` | (Optional) Worker node GPU limit.           | -                                 |
   | `workerGroup.affinity.gpuClass`         | (Optional) GPU class for workers.           | -                                 |
   | `workerGroup.affinity.region`           | (Optional) Region for workers.              | -                                 |

1. Install the Helm Chart:

   ```console
   user@host:~/lumigator$ helm install inference-service ./infra/helm/inference-service
   ```

   ```{note}
   Depending on the model you're trying to deploy this step may take a while to complete.
   ```

## Verify

1. Port-forward the Ray dashboard:

   ```console
   user@host:~/lumigator$ kubectl port-forward svc/inference-service-ray-dashboard 8265:8265
   ```

   Navigate to `http://localhost:8265` to access the Ray dashboard. Check that the Ray Serve deployment is running
   and the GPU resources are allocated correctly.

   ```{note}
   The name of the service may vary depending on the name you've chosen for the Ray Service.
   ```

1. Port-forward the head node of the Ray cluster:

   ```
   user@host:~/lumigator$ kubectl port-forward pod/inference-service-ray-head-0 8080:8000
   ```

   ```{note}
   The name of the pod may vary depending on the name you've chosen for the Ray Service.
   ```

1. Invoke the model:

   ```console
   user@host:~/lumigator$ curl "http://localhost:8080/v1/chat/completions" -H "Content-Type: application/json" -d '{"model": "<model-name>", "messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello!"}]}'
   ```

   The response should be a JSON object with the model's prediction.

   ```{note}
   Replace `<model-name>` with the name of the model you've deployed.
   ```

## Conclusion

You've successfully deployed a vLLM-supported model using Ray Serve on a Kubernetes cluster. You can now use the model
for inference and explore advanced configurations like tensor parallelism, pipeline parallelism, and LoRA modules.
