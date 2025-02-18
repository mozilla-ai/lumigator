# Mozilla.ai Lumigator Frontend Helm chart

This Helm chart is the official way to deploy the Lumigator application Frontend in cloud environments with Kubernetes.

This Helm chart deploys the Lumigator Frontend built with Vue 3, and Vite, and designed to interact with the REST API provided by the Lumigator backend.

## Frontend Values

| Key | Default | Description |
|-----|---------|-------------|
| fullnameOverride | `""` | - |
| image.pullPolicy | `"IfNotPresent"` | The Kubernetes [imagePullPolicy](https://kubernetes.io/docs/concepts/containers/images/#updating-images) value |
| image.repository | `"mzdotai/lumigator-frontend"` | Repository where the Lumigator Frontend image is located |
| image.tag | `"v0.1.1-alpha"` | The Lumigator Frontend Docker image tag |
| imagePullSecrets | `[]` | Setting to pull an image from a private repository more information can be found [here](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) |
| livenessProbe.httpGet.path | `"/"` | Path against the liveness probe to be executed |
| livenessProbe.httpGet.port | `"http"` | Port against the liveness probe to be executed |
| nameOverride | `""` | - |
| podLabels | `{}` | Kubernetes labels to be set on the pods |
| podSecurityContext | `{}` | Security settings applied to the pod |
| readinessProbe.httpGet.path | `"/"` | Path against the readiness probe to be executed |
| readinessProbe.httpGet.port | `"http"` | Port against the readiness probe to be executed |
| replicaCount | `1` | Number of replicas to be set in the replicaset |
| resources | `{}` | Resources assigned to the Lumigator Frontend pod |
| securityContext | `{}` | Security settings applied to the Lumigator container |
| service.port | `80` | Port for the http service |
| service.type | `"ClusterIP"` | Type of the [Kubernetes service](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) to use |
| serviceAccountName | `""` | ServiceAccount that the Pod will use to access the Kubernetes API and other resources |

----------------------------------------------

This list of variables was generated with [`helm-docs`](https://github.com/norwoodj/helm-docs)
