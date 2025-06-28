{{/* vim: set filetype=mustache: */}}
{{- define "morvo.fullname" -}}
{{ include "morvo.name" . }}
{{- end -}}

{{- define "morvo.name" -}}
{{ .Chart.Name }}
{{- end -}}

{{- define "morvo.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "morvo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "morvo.name" . }}
{{- end -}} 