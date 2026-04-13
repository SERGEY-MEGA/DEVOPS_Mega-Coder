# --- builder: ставим Python-зависимости в отдельный venv ---------------------
# Multi-stage build нужен по ТЗ: в runtime попадёт только готовое приложение.
FROM python:3.12.8-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- runtime: минимальный slim-образ и непривилегированный пользователь -------
FROM python:3.12.8-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# UID/GID фиксируем явно, чтобы Kubernetes runAsNonRoot был предсказуемым.
RUN groupadd --system --gid 10002 app \
    && useradd --system --uid 10002 --gid 10002 --home-dir /app --no-create-home app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app ./app

USER 10002:10002

EXPOSE 8088

# Healthcheck нужен для Kubernetes liveness/readiness и для демонстрации.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8088"]
