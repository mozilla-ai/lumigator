# Deploy DeepSeek V3/R1

This guide will walk you through deploying DeepSeek V3/R1 on a Kubernetes cluster.

## What you'll need

To complete this guide, you'll need:

- Access to a Kubernetes cluster.
- At least 32 A100s (80GB) or 16 H100s (80GB).

## Procedure

The following procedure demonstrates how to deploy DeepSeek V3 (BF16 variant) on a Kubernetes cluster. The deployment
process for any R1 variant is similar.

1. Create a PVC to download the model to:

    ```bash
    kubectl apply -f pvc.yaml
    ```

1. Create a pod and mount the PVC:

    ```bash
    kubectl apply -f downloader.yaml
    ```

1. Exec into the pod and navigate to the `models` directory:

    ```bash
    kubectl exec -it hf-downloader -- /bin/bash
    cd /mnt/models
    ```

1. Git clone the model (this step will take a few hours):

    ```bash
    apt install git-lfs
    git lfs install
    git clone https://huggingface.co/deepseek-ai/DeepSeek-V3-bf16
    ```

    > [!NOTE]
    > The original DeepSeek V3 model is natively trained in FP8 precision. Our on-prem cluster's A100s are not
    > [supported](https://github.com/vllm-project/vllm/issues/11539#issuecomment-2566596112). On the official repo they
    > provide a script to cast FP8 to BF16 and someone has already done this:
    > https://huggingface.co/opensourcerelease/DeepSeek-V3-bf16/tree/main

1. Create the Ray Service:

    ```bash
    kubectl apply -f deepseek-v3-bf16.yaml
    ```

    > [!NOTE]
    > The server will take several minutes to complete.

1. Port-forward the pod that runs the head node:

    ```bash
    kubectl port-forward po/deepseek-v3-cluster-head-<random-hash> 8080:8000
    ```

1. Invoke the model:

    ```bash
    curl "http://localhost:8080/v1/chat/completions" \
          -H "Content-Type: application/json" \
          -d '{
                "model": "DeepSeek-V3",
                "messages": [
                  {
                      "role": "system",
                      "content": "You are a helpful assistant."
                  },
                  {
                      "role": "user",
                      "content": "What is Kubernetes?"
                  }
                ]
              }'
    ```
