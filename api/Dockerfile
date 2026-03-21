# --- Этап 1: builder — ставим зависимости и готовим venv ----------------------
# Используем фиксированную версию образа (не latest), как рекомендует ТЗ.
FROM python:3.12.8-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Системные зависимости только для сборки wheel'ей (минимум пакетов).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Этап 2: runtime — минимальный образ, приложение не от root --------------
FROM python:3.12.8-alpine3.21 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Непривилегированный пользователь (ТЗ: не root).
RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

# Копируем только venv из builder (слои остаются компактными).
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app ./app

USER app

EXPOSE 8000

# Проверка здоровья контейнера (рекомендация ТЗ).
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# Запуск uvicorn на всех интерфейсах — внутри Pod это безопасно, наружу идёт Service.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
