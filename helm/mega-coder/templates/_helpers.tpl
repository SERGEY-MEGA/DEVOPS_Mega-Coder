{{/*
Имена ресурсов и сборка ссылки на образ.
Для api/web/worker используется global.imageRegistry (GitLab Registry).
Для redis — поле imageRegistry у компонента (Docker Hub), чтобы не пушить чужой образ в GitLab.
*/}}
{{- define "mega-coder.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "mega-coder.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end }}

{{- define "mega-coder.image" -}}
{{- $root := index . "root" -}}
{{- $img := index . "image" -}}
{{- if $img.imageRegistry -}}
{{- printf "%s/%s:%s" $img.imageRegistry $img.repository $img.tag -}}
{{- else if $root.Values.global.imageRegistry -}}
{{- printf "%s/%s:%s" $root.Values.global.imageRegistry $img.repository $img.tag -}}
{{- else -}}
{{- printf "%s:%s" $img.repository $img.tag -}}
{{- end -}}
{{- end }}
