# Install Lumigator on Kubernetes

This guide will walk you through the process of installing Lumigator on a Kubernetes cluster.
The official way to deploy the Lumigator application in cloud environments with Kubernetes is to use
the Helm package manager.

At this moment this Helm chart deploys the Lumigator core REST API (backend) and the Lumigator frontend. Additionally, by default, it also deploys a Ray cluster with a postgres instance as a dependency of the backend.

If you want to use your existent relational database instance or Ray cluster, you will have to reconfigure the dependencies of the backend chart.

We don't provide support for Ray, S3-compatible storage, or the database which are required for the full application to run. In
the near future, a new version of this chart will be released, which will be able to deploy a
minimal version of all the required tools.

```{warning}
Lumigator needs an existing: S3 bucket, relational database and a Ray cluster in order to work as
expected.
```

## Prerequisites

To install Lumigator on a Kubernetes cluster, you need to have the following prerequisites:

- A Kubernetes cluster running.
- Helm installed in your Kubernetes cluster.
- A S3-compatible storage bucket.
- A relational database.
- A Ray cluster.

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
    ```

## Configuration

The following table lists the configurable parameters of the Lumigator chart and their default
values. On top of these, If the Mistral and/or the OpenAI API is used, there are two ways to provide
it to Lumigator:

- Using an existing Secret, whose name will be specified in property `existingMistralAPISecret`
  and/or `existingOpenaiAPISecret`
- Using an explicit Mistral and/or OpenAI key in property `mistralAPIKey` and/or `openaiAPIKey`,
  which will be added in a new Secret.

| Key                        | Default          | Description                                                                                                                                                                                                               |
|----------------------------|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `affinity`                 | `{}`             | Kubernetes rules for [scheduling Pods on specific nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)                                                             |
| `fullnameOverride`         | `""`             | -                                                                                                                                                                                                                         |
| `image.pullPolicy`         | `"IfNotPresent"` | The Kubernetes [imagePullPolicy](https://kubernetes.io/docs/concepts/containers/images/#updating-images) value                                                                                                            |
| `image.repository`         | `""`             | Repository where the Lumigator image is located                                                                                                                                                                           |
| `image.tag`                | `"1"`            | The Lumigator Docker image tag                                                                                                                                                                                            |
| `imagePullSecrets`         | `[]`             | Configuration for [imagePullSecrets](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret) so that you can use a private registry for your image      |
| `nameOverride`             | `""`             | -                                                                                                                                                                                                                         |
| `nodeSelector`             | `{}`             | Configurable [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) so that you can target specific nodes                                                                  |
| `podAnnotations`           | `{}`             | Configurable [annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) applied to all pods                                                                                            |
| `podSecurityContext`       | `{}`             | Security settings applied to the pod                                                                                                                                                                                      |
| `existingMistralAPISecret` | ``               | Name of an existing [Secret](https://kubernetes.io/docs/concepts/configuration/secret/) that contains the Mistral key                                                                                                     |
| `mistralAPIKey`            | ``               | Mistral key to be added as a [Secret](https://kubernetes.io/docs/concepts/configuration/secret/)                                                                                                                          |
| `existingOpenaiAPISecret`  | ``               | Name of an existing [Secret](https://kubernetes.io/docs/concepts/configuration/secret/) that contains the OpenAI key                                                                                                      |
| `openaiAPIKey`             | ``               | OpenAI key to be added as a [Secret](https://kubernetes.io/docs/concepts/configuration/secret/)                                                                                                                           |
| `rayAddress`               | `""`             | URL of the Ray cluster                                                                                                                                                                                                    |
| `rayPort`                  | `""`             | Port of the Ray cluster                                                                                                                                                                                                   |
| `rayWorkerGPUs`            | `""`             | Amount of GPUs that each Ray worker is going to use                                                                                                                                                                       |
| `replicaCount`             | `1`              | Lumigator API replicas                                                                                                                                                                                                    |
| `resources`                | `{}`             | Resources assigned to the Lumigator pod                                                                                                                                                                                   |
| `s3Bucket`                 | `""`             | URL of the S3-compatible storage system                                                                                                                                                                                   |
| `securityContext`          | `{}`             | Security settings applied to the Lumigator container                                                                                                                                                                      |
| `service.annotations`      | `{}`             | [LoadBalancer](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) annotations that Kubernetes will use for the service. This will configure load balancer if `service.type` is `LoadBalancer` |
| `service.https`            | `false`          | Enables https traffic for the service on port 443                                                                                                                                                                         |
| `service.port`             | `80`             | Port for the HTTP service                                                                                                                                                                                                 |
| `service.type`             | `"ClusterIP"`    | Type of the [Kubernetes service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to use                                                                               |
| `serviceAccountName`       | `""`             | [ServiceAccount](https://kubernetes.io/docs/concepts/security/service-accounts/) that the Pod will use to access the Kubernetes API and other resources                                                                   |
| `tolerations`              | `[]`             | Configurable Kubernetes [tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)                                                                                                      |

## Next Steps

Congratulations! You have successfully installed Lumigator on your Kubernetes cluster. Now you can
start using it to evaluate your language models. Head over to the user guides to learn how to
interact with the Lumigator API to create new evaluation jobs.
