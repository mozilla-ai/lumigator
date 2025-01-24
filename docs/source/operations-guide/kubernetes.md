# Install Lumigator on Kubernetes

This guide will walk you through the process of installing Lumigator on a Kubernetes cluster.
The official way to deploy the Lumigator application in cloud environments with Kubernetes is to use
the Helm package manager.

```{warning}
Lumigator needs an existing: S3 bucket, and a Ray cluster in order to work as expected.
```

## Prerequisites

To install Lumigator on a Kubernetes cluster, you need to have the following prerequisites:

- A Kubernetes cluster running.
- Helm
- A S3-compatible storage bucket.
- A Ray cluster.

## Helm Values
Example helm values are provided below

```
backend:
  s3Bucket: "lumigator-ktest"
  AWSAccessKey: "your-aws-acces-key"
  AWSSecretKey: "your-aws-secret-key"

  rayAddress: address-of-your-ray-cluster
  rayWorkerGPUs: "1.0" # The number of GPUs you'd like to use in requests to your ray cluster
```

## Installation

To install Lumigator on a Kubernetes cluster, follow these steps:

1. Clone the Lumigator repository:

    ```console
    user@host:~$ git clone git@github.com:mozilla-ai/lumigator.git
    ```

1. Change to the Lumigator directory:

    ```console
    user@host:~$ cd lumigator
    ```

1. Install the Lumigator Helm chart:

    ```console
    user@host:~/lumigator$ helm install lumigator ./lumigator/infra/mzai/helm/lumigator
    helm install lumigator lumigator --set backend.image.tag=backend_dev_c107c4c,frontend.image.tag=frontend_09799ee -f cw-values.yaml
    ```

## Configuration

The following table lists the configurable parameters of the Lumigator chart and their default
values. On top of these, If the Mistral and/or the OpenAI API is used, there are two ways to provide
it to Lumigator:

- Using an existing Secret, whose name will be specified in property `existingMistralAPISecret`
  and/or `existingOpenaiAPISecret`
- Using an explicit Mistral and/or OpenAI key in property `mistralAPIKey` and/or `openaiAPIKey`,
  which will be added in a new Secret.

## Uninstallation
Note: When uninstalling lumigator, you must manually remove the postgres pvc

## Next Steps

Congratulations! You have successfully installed Lumigator on your Kubernetes cluster. Now you can
start using it to evaluate your language models. Head over to the user guides to learn how to
interact with the Lumigator API to create new evaluation jobs.
