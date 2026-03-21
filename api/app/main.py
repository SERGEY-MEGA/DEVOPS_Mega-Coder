"""
Основной HTTP-сервис (backend) стека MEGA CODER.

Назначение файла:
- предоставить REST API и /health для проверок Kubernetes/GitLab CI;
- читать конфигурацию только из переменных окружения (параметризация по ТЗ);
- опционально проверять доступность Redis (третий сервис в архитектуре).
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import redis
from fastapi import FastAPI

# --- Параметризация через переменные окружения (описаны в REPORT.md) ---
SERVICE_NAME = os.getenv("SERVICE_NAME", "api")
LISTEN_HOST = os.getenv("LISTEN_HOST", "0.0.0.0")
LISTEN_PORT = int(os.getenv("LISTEN_PORT", "8000"))
REDIS_URL = os.getenv("REDIS_URL", "")  # например redis://redis:6379/0
WORKER_BASE_URL = os.getenv("WORKER_BASE_URL", "http://worker:8081")

app = FastAPI(title="MEGA CODER API", version="1.0.0")


def _redis_ping() -> dict[str, Any]:
    """Проверка Redis; при отсутствии REDIS_URL возвращаем skipped."""
    if not REDIS_URL:
        return {"status": "skipped", "reason": "REDIS_URL is empty"}
    try:
        client = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=2)
        ok = client.ping()
        return {"status": "ok" if ok else "fail"}
    except Exception as exc:  # noqa: BLE001 — хотим отчёт в health, не падаем
        return {"status": "error", "detail": str(exc)}


@app.get("/health")
def health() -> dict[str, Any]:
    """
    Liveness/readiness: быстрый ответ без внешних зависимостей.
    Детальные проверки — в /ready.
    """
    return {"service": SERVICE_NAME, "status": "ok"}


@app.get("/ready")
def ready() -> dict[str, Any]:
    """Готовность: Redis (если задан) и worker-сервис отвечают."""
    worker: dict[str, Any] = {"status": "skipped"}
    try:
        r = httpx.get(f"{WORKER_BASE_URL}/health", timeout=2.0)
        worker = {"status": "ok" if r.status_code == 200 else "fail", "code": r.status_code}
    except Exception as exc:  # noqa: BLE001
        worker = {"status": "error", "detail": str(exc)}

    return {
        "service": SERVICE_NAME,
        "redis": _redis_ping(),
        "worker": worker,
    }


@app.get("/api/info")
def info() -> dict[str, Any]:
    """Демонстрационный бизнес-эндпоинт для фронтенда и отчёта."""
    return {
        "message": "MEGA CODER API",
        "service": SERVICE_NAME,
        "frontend_hint": "Откройте веб-интерфейс — он дергает этот метод.",
    }
