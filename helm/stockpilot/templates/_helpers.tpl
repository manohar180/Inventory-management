{{/*
_helpers.tpl — Shared template helpers for StockPilot Helm chart
WHY:  DRY (Don't Repeat Yourself) — define name/label logic once, use everywhere.
      If the release name changes, every resource updates automatically.
*/}}

{{/* Full name: <release>-stockpilot (trimmed to 63 chars — k8s limit) */}}
{{- define "stockpilot.fullname" -}}
{{- printf "%s-stockpilot" .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Chart label: stockpilot-1.0.0 */}}
{{- define "stockpilot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Standard labels applied to every resource */}}
{{- define "stockpilot.labels" -}}
helm.sh/chart: {{ include "stockpilot.chart" . }}
app.kubernetes.io/name: stockpilot
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Backend selector labels */}}
{{- define "stockpilot.backendSelectorLabels" -}}
app.kubernetes.io/name: stockpilot
app.kubernetes.io/component: backend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Frontend selector labels */}}
{{- define "stockpilot.frontendSelectorLabels" -}}
app.kubernetes.io/name: stockpilot
app.kubernetes.io/component: frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
