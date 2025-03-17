# Mozilla.ai Lumigator Backend Helm chart

This Helm chart is the official way to deploy the Lumigator application in cloud environments with Kubernetes

This Helm chart deploys the Lumigator core REST API, Ray cluster and postgres. You will need to add your own S3 compatible object storage to run the app.

> [!WARNING]
> We don't provide support for Ray, S3-compatible storage, or Postgres which are required for the full application to run.

## DeepSeek, Mistral and OpenAI API key management

If you want Lumigator to be able to access hosted API-based LLM services such as OpenAI, DeepSeek or Mistral, you'll need
to configure those secrets in Lumigator once it's running.

Refer to [API settings configuration](../operations-guide/configuration#api-settings) for more details.

## Backend Values

| Key                         | Default               | Description                                                                                                                                                                                                          |
|-----------------------------|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| fullnameOverride            | `""`                  | -                                                                                                                                                                                                                    |
| image.pullPolicy            | `"IfNotPresent"`      | The Kubernetes [imagePullPolicy](https://kubernetes.io/docs/concepts/containers/images/#updating-images) value                                                                                                       |
| image.repository            | `"mzdotai/lumigator"` | Repository where the Lumigator image is located                                                                                                                                                                      |
| image.tag                   | `"v0.1.2-alpha"`      | The Lumigator Docker image tag                                                                                                                                                                                       |
| imagePullSecrets            | `[]`                  | Configuration for [imagePullSecrets](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret) so that you can use a private registry for your image |
| nameOverride                | `""`                  | -                                                                                                                                                                                                                    |
| podSecurityContext          | `{}`                  | Security settings applied to the pod                                                                                                                                                                                 |
| postgresDb                  | `""`                  | Name of the database                                                                                                                                                                                                 |
| postgresHost                | `""`                  | URL of the database                                                                                                                                                                                                  |
| postgresPassword            | `""`                  | Password of the user used to connect to the database                                                                                                                                                                 |
| postgresPort                | `""`                  | Port of the database                                                                                                                                                                                                 |
| postgresUser                | `""`                  | User to connect to the database                                                                                                                                                                                      |
| rayAddress                  | `""`                  | URL of the Ray cluster                                                                                                                                                                                               |
| rayPort                     | `""`                  | Port of the Ray cluster                                                                                                                                                                                              |
| rayWorkerGPUs               | `""`                  | Amount of GPUs that each Ray worker is going to use                                                                                                                                                                  |
| resources                   | `{}`                  | Resources assigned to the Lumigator pod                                                                                                                                                                              |
| s3Bucket                    | `""`                  | URL of the S3-compatible storage system                                                                                                                                                                              |
| securityContext             | `{}`                  | Security settings applied to the Lumigator container                                                                                                                                                                 |
| service.annotations         | `{}`                  | LoadBalancer annotations that Kubernetes will use for the service. This will configure load balancer if service.type is LoadBalancer                                                                                 |
| service.port                | `80`                  | Port for the http service                                                                                                                                                                                            |
| service.type                | `"ClusterIP"`         | Type of the [Kubernetes service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to use                                                                          |
| serviceAccountName          | `""`                  | ServiceAccount that the Pod will use to access the Kubernetes API and other resources                                                                                                                                |
----------------------------------------------

This list of variables was generated with [`helm-docs`](https://github.com/norwoodj/helm-docs)
