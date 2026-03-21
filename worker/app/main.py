"""
Второй backend-сервис (worker API) — лёгкий HTTP-микросервис.

Зачем отдельный сервис по ТЗ:
- в стеке должно быть минимум три сервиса (BE, FE, вспомогательный);
- даёт простую цепочку вызовов api -> worker для демонстрации сети в Kubernetes;
- конфигурируется через переменные окружения.
"""

import os

from fastapi import FastAPI

SERVICE_NAME = os.getenv("SERVICE_NAME", "worker")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "8081"))

app = FastAPI(title="MEGA CODER Worker", version="1.0.0")


@app.get("/health")
def health() -> dict:
    """Проверка для Kubernetes и для /ready основного API."""
    return {"service": SERVICE_NAME, "status": "ok"}


@app.get("/work/ping")
def ping() -> dict:
    """Простой «рабочий» маршрут для нагрузочных/демо запросов."""
    return {"service": SERVICE_NAME, "echo": "pong"}
