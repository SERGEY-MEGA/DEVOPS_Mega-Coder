# builder: ставим зависимости в отдельный слой, чтобы runtime-образ был меньше и чище.
FROM python:3.12.8-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
# Virtualenv переносится в runtime целиком и не смешивается с системным Python.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# Все Python-пакеты собираются на этапе builder.
RUN pip install --upgrade pip && pip install -r requirements.txt

# runtime: slim-слой совместим с пакетами, собранными в builder на Debian base.
FROM python:3.12.8-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Сервис запускается не от root; UID/GID фиксируем явно для Kubernetes securityContext.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --home-dir /app --no-create-home app
WORKDIR /app

# Копируем только то, что реально нужно для запуска: venv и исходники.
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app ./app

USER 10001:10001
EXPOSE 8081

# Healthcheck потом удобно использовать и в Docker, и в Kubernetes probes.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/health')"

# Worker слушает свой отдельный HTTP-порт, чтобы API ходил к нему через Kubernetes Service.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
