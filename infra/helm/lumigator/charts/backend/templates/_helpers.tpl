{{/*
Expand the name of the chart.
*/}}
{{- define "lumigator.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "lumigator.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "lumigator.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Return lumigator repo
*/}}
{{- define "lumigator.repo" -}}
{{- required "The repository for the Lumigator image is missing" .Values.image.repository }}
{{- end }}

{{/*
Return lumigator tag
*/}}
{{- define "lumigator.tag" -}}
{{- .Values.image.tag | default .Chart.AppVersion | required "The tag for the Lumigator image is missing" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "lumigator.labels" -}}
helm.sh/chart: {{ include "lumigator.chart" . }}
{{ include "lumigator.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "lumigator.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lumigator.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Generated Secret name for Mistral
*/}}
{{- define "lumigator.mistral-secret-name" -}}
{{- include "lumigator.name" . -}}-mistral
{{- end }}

{{- define "lumigator.mistral-secret-ref" -}}
  {{ if .Values.existingMistralAPISecret }}
    {{- .Values.existingMistralAPISecret }}
  {{- else -}}
    {{- include "lumigator.mistral-secret-name" . }}
  {{- end }}
{{- end }}

{{- define "lumigator.mistral-default-secret" -}}
{{- $_ := set . "Consts" (dict)  -}}
{{- $_ := set .Consts "mistralSecretKey" "MISTRAL_API_KEY" -}}
{{- end -}}

{{/*
Generated Secret name for OpenAI
*/}}
{{- define "lumigator.openai-secret-name" -}}
{{- include "lumigator.name" . -}}-openai
{{- end }}

{{- define "lumigator.openai-secret-ref" -}}
  {{ if .Values.existingOpenaiAPISecret }}
    {{- .Values.existingOpenaiAPISecret }}
  {{- else -}}
    {{- include "lumigator.openai-secret-name" . }}
  {{- end }}
{{- end }}

{{- define "lumigator.openai-default-secret" -}}
{{- $_ := set . "Consts" (dict)  -}}
{{- $_ := set .Consts "openaiSecretKey" "OPENAI_API_KEY" -}}
{{- end -}}

{{- define "lumigator.ray-address" -}}
{{- if .Values.rayAddress }}
{{- .Values.rayAddress }}
{{- else }}
{{- include "ray-cluster.fullname" (index .Subcharts "ray-cluster") }}-head-svc
{{- end }}
{{- end -}}

{{- define "lumigator.mlflow-address" -}}
{{- if .Values.mlFlowAddress }}
{{- .Values.mlFlowAddress }}
{{- else }}
{{- include "mlflow.fullname" (index .Subcharts "mlflow") }}
{{- end }}
{{- end -}}
