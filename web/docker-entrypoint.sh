#!/bin/sh
# 1) Читаем шаблон nginx и подставляем PORT / API_UPSTREAM из env (параметризация).
# 2) Пишем итоговый конфиг в /tmp (доступно процессу nginx).
# 3) Запускаем nginx от пользователя nginx через su-exec (соответствие ТЗ: не root).
set -eu
export PORT="${PORT:-8080}"
export API_UPSTREAM="${API_UPSTREAM:-http://api:8000}"
envsubst '${PORT} ${API_UPSTREAM}' < /etc/nginx/nginx.conf.template > /tmp/nginx.conf
exec su-exec nginx nginx -c /tmp/nginx.conf -g "daemon off;"
