# builder: сохраняем только шаблон конфигурации.
FROM nginx:1.27.3-alpine3.20 AS builder
WORKDIR /tmp
COPY nginx.conf /tmp/nginx.conf.template

# runtime: alpine + gettext для envsubst, без лишних root-переходов на старте.
FROM nginx:1.27.3-alpine3.20 AS runtime

# gettext нужен для envsubst, wget — для healthcheck.
RUN apk add --no-cache gettext wget

COPY --from=builder /tmp/nginx.conf.template /etc/nginx/nginx.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY html /usr/share/nginx/html

# Подготавливаем права и временные директории, чтобы nginx мог работать без root-привилегий.
RUN chmod +x /docker-entrypoint.sh \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx \
    && install -d -o nginx -g nginx /tmp/nginx-client-body

# Фиксируем числовой UID/GID стандартного пользователя nginx, чтобы Pod с runAsNonRoot стартовал предсказуемо.
USER 101:101

EXPOSE 8080

# Проверяем именно корневой URL, потому что это основной пользовательский вход в приложение.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ || exit 1

# ENTRYPOINT нужен, чтобы перед стартом nginx собрать итоговый конфиг из шаблона.
ENTRYPOINT ["/docker-entrypoint.sh"]
