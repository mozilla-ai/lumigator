{{/*
Create a default app name and namespace.
Truncate at 63 chars since Kubernetes name fields are limited by the DNS naming spec.
*/}}
{{- define "inference-service.name" -}}
{{- default .Chart.Name .Values.inferenceServiceName | trunc 63 | trimSuffix "-" }}
{{- end}}
