# builder: сохраняем только шаблон конфигурации.
FROM nginx:1.27.3-alpine3.20 AS builder
WORKDIR /tmp
COPY nginx.conf /tmp/nginx.conf.template

# runtime: alpine + gettext (envsubst) + su-exec (сброс прав на nginx).
FROM nginx:1.27.3-alpine3.20 AS runtime

RUN apk add --no-cache gettext su-exec wget

COPY --from=builder /tmp/nginx.conf.template /etc/nginx/nginx.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY html /usr/share/nginx/html

RUN chmod +x /docker-entrypoint.sh \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx \
    && install -d -o nginx -g nginx /tmp/nginx-client-body

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
