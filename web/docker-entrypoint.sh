#!/bin/sh
# 1) Читаем шаблон nginx и подставляем PORT / API_UPSTREAM из env (параметризация).
# 2) Пишем итоговый конфиг в /tmp (доступно процессу nginx).
# 3) Запускаем nginx напрямую от уже непривилегированного пользователя контейнера.
set -eu
# Значения по умолчанию позволяют запускать контейнер и локально, не только в Kubernetes.
export PORT="${PORT:-8080}"
export API_UPSTREAM="${API_UPSTREAM:-http://api:8000}"
# Из шаблона собирается итоговый nginx.conf с конкретным портом и upstream.
envsubst '${PORT} ${API_UPSTREAM}' < /etc/nginx/nginx.conf.template > /tmp/nginx.conf
# Основной процесс контейнера — nginx в foreground.
exec nginx -c /tmp/nginx.conf -g "daemon off;"
