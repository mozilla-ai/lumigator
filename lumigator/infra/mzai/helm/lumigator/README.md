# Mozilla.ai Lumigator Helm chart

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

This Helm chart is the official way to deploy the Lumigator application in cloud environments with Kubernetes

At this moment this Helm chart only deploys Lumigator, we don't provide any default solution for 3rd party tools needed for the correct behavior of Lumigator (like S3 buckets, relational databases, etc).

> [!WARNING]  
> Lumigator needs an existent: S3 bucket, a relational database and a Ray cluster in order to work as expected.

In the near future, a new version of this chart will be released, which will be able to deploy a minimal version of all the required tools.

## Values

| Key | Default | Description |
|-----|---------|-------------|
| affinity | `{}` |  Kubernetes rules for [scheduling Pods on specific nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) |
| fullnameOverride | `""` | - |
| image.pullPolicy | `"IfNotPresent"` | The Kubernetes [imagePullPolicy](https://kubernetes.io/docs/concepts/containers/images/#updating-images) value |
| image.repository | `""` | Repository where the Lumigator image is located |
| image.tag | `"1"` | The Lumigator Docker image tag |
| imagePullSecrets | `[]` | Configuration for [imagePullSecrets](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret) so that you can use a private registry for your image |
| nameOverride | `""` | - |
| nodeSelector | `{}` | Configurable [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) so that you can target specific nodes |
| podAnnotations | `{}` | Configurable [annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) applied to all pods |
| podSecurityContext | `{}` | Security settings applied to the pod |
| postgresDb | `""` | Name of the database |
| postgresHost | `""` | URL of the database |
| postgresPassword | `""` | Password of the user used to connect to the database |
| postgresPort | `""` | Port of the database |
| postgresUser | `""` | User to connect to the database |
| rayAddress | `""` | URL of the Ray cluster |
| rayPort | `""` | Port of the Ray cluster |
| rayWorkerGPUs | `""` | Amount of GPUs that each Ray worker is going to use |
| replicaCount | `1` | Lumigator API replicas |
| resources | `{}` | Resources assigned to the Lumigator pod |
| s3Bucket | `""` | URL of the S3 bucket |
| securityContext | `{}` | Security settings applied to the Lumigator container |
| service.annotations | `{}` | LoadBalancer annotations that Kubernetes will use for the service. This will configure load balancer if service.type is LoadBalancer | 
| service.https | `false` | Enables https traffic for the service on port 443 |
| service.port | `80` | Port for the http service |
| service.type | `"ClusterIP"` | Type of the [Kubernetes service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to use |
| serviceAccountName | `""` | ServiceAccount that the Pod will use to access the Kubernetes API and other resources |
| summarizerWorkDir | `""` | S3 folder where the summarizer is located |
| tolerations | `[]` | Configurable Kubernetes [tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) |