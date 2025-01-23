# Mozilla.ai Lumigator Helm chart

This Helm chart is the official way to deploy the Lumigator application in cloud environments with Kubernetes

This Helm chart deploys the Lumigator core REST API, frontend and postgres. You will need to add your own Ray cluster and S3 compatible object storage to run the app.

## Mistral/OpenAI API key management

If the Mistral and/or the OpenAI API is used, there are two ways to provide it to Lumigator:

* Using an existing Secret, whose name will be specified in property `backend.existingMistralAPISecret` and/or `backend.existingOpenaiAPISecret`
* Using an explicit Mistral and/or OpenAI key in property `backend.mistralAPIKey` and/or `backend.openaiAPIKey`, which will be added in a new Secret

> [!NOTE]
> Both properties cannot be set at the same time.

## Backend Values

| Key | Default | Description |
|-----|---------|-------------|
| backend.image.pullPolicy | `"IfNotPresent"` | The Kubernetes [imagePullPolicy](https://kubernetes.io/docs/concepts/containers/images/#updating-images) value |
| backend.image.repository | `""` | Repository where the Lumigator image is located |
| backend.image.tag | `"1"` | The Lumigator Docker image tag |
| backend.imagePullSecrets | `[]` | Configuration for [imagePullSecrets](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-pod-that-uses-your-secret) so that you can use a private registry for your image |
| backend.podSecurityContext | `{}` | Security settings applied to the pod |
| backend.existingMistralAPISecret | `` | Name of an existing Secret that contains the Mistral key |
| backend.mistralAPIKey | `` | Mistral key to be added as a Secret |
| backend.existingOpenaiAPISecret | `` | Name of an existing Secret that contains the OpenAI key |
| backend.openaiAPIKey | `` | OpenAI key to be added as a Secret |
| backend.postgresDb | `""` | Name of the database |
| backend.postgresHost | `""` | URL of the database |
| backend.postgresPassword | `""` | Password of the user used to connect to the database |
| backend.postgresPort | `""` | Port of the database |
| backend.postgresUser | `""` | User to connect to the database |
| backend.rayAddress | `""` | URL of the Ray cluster |
| backend.rayPort | `""` | Port of the Ray cluster |
| backend.rayWorkerGPUs | `""` | Amount of GPUs that each Ray worker is going to use |
| backend.resources | `{}` | Resources assigned to the Lumigator pod |
| backend.s3Bucket | `""` | URL of the S3-compatible storage system |
| backend.securityContext | `{}` | Security settings applied to the Lumigator container |
| backend.service.annotations | `{}` | LoadBalancer annotations that Kubernetes will use for the service. This will configure load balancer if service.type is LoadBalancer |
| backend.service.port | `80` | Port for the http service |
| backend.service.type | `"ClusterIP"` | Type of the [Kubernetes service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to use |
| backend.serviceAccountName | `""` | ServiceAccount that the Pod will use to access the Kubernetes API and other resources |
