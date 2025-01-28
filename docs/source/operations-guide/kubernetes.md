# Install Lumigator on Kubernetes

This guide will walk you through the process of installing Lumigator on a Kubernetes cluster.
The official way to deploy the Lumigator application in cloud environments with Kubernetes is to use
the Helm package manager.

At this moment this Helm chart deploys the Lumigator core REST API (backend) and the Lumigator frontend. Additionally, by default, it also deploys a Ray cluster with a postgres instance as a dependency of the backend.

If you want to use your existent relational database instance or Ray cluster, you will have to reconfigure the dependencies of the backend chart.

## Prerequisites

To install Lumigator on a Kubernetes cluster, you need to have the following prerequisites:

- A Kubernetes cluster running.
- A S3-compatible storage bucket.
- Helm installed.

## Configuration

The Lumigator chart is composed of two sub-charts, backend and frontend. The main Lumigator one is
designed to deploy everything you need with a single command, and only include in the values file
those values that are required to make the sub charts work together (like the address of Ray).

By default, the backend chart also deploys a PostgreSQL instance, and a Ray cluster into Kubernetes,
with a minimal configuration ready to work with Lumigator.

> [!NOTE]If the Mistral and/or the OpenAI API is used, there are two ways to provide
> it to Lumigator:
>
> - Using an existing Secret, whose name will be specified in property `existingMistralAPISecret`
>   and/or `existingOpenaiAPISecret`
> - Using an explicit Mistral and/or OpenAI key in property `mistralAPIKey` and/or `openaiAPIKey`,
>   which will be added in a new Secret.

In order to be able to use Mistral and/or the OpenAI API, you also have to add this configuration to your values file:

```console
ray-cluster:
  head:
    containerEnv:
      - name: MISTRAL_API_KEY
            valueFrom: "name-of-the-mistral-secret"
              secretKeyRef: "name-of-the-mistral-secret-key"
      - name: OPENAI_API_KEY
            valueFrom: "name-of-the-openai-secret"
              secretKeyRef: "name-of-the-openai-secret-key"
```

## Example values configurations

This is just a minimal example of the values that you have to set in the values files of the backend chart in order
to make Lumigator work as expected:

Backend:
```console
s3Bucket: "example-bucket-name"  # Name of the S3 bucket you want to use.
AWSAccessKey: "EXAMPLE_AWS_ACCESS_KEY"  # AWS access key.
AWSSecretKey: "EXAMPLE_AWS_SECRET_KEY"  # AWS secret key.
rayAddress: "example-ray-cluster-head-address"  # Address of the Ray cluster head service. If you use the Ray cluster deployed with the backend chart, the value is the first word of your helm release name + -lumigator-kuberay-head-svc

ray-cluster:
  head:
    containerEnv:
      - name: FSSPEC_S3_KEY
        value: "example-s3-key"  # S3 access key used by containers.
      - name: FSSPEC_S3_SECRET
        value: "example-s3-secret"  # S3 secret key used by containers.
      - name: FSSPEC_S3_ENDPOINT_URL
        value: "https://example-s3-endpoint.com"  # S3 endpoint URL used by containers.
```

Save this example as a `values.yaml` file, customize it with your own values, and you can proceed to install Lumigator following the steps describe in the next section.

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
    user@host:~/lumigator$ helm install lumigator ./infra/helm/lumigator -f values.yaml
    ```

## Next Steps

Congratulations! You have successfully installed Lumigator on your Kubernetes cluster. Now you can
start using it to evaluate your language models. Head over to the user guides to learn how to
interact with the Lumigator API to create new evaluation jobs.
