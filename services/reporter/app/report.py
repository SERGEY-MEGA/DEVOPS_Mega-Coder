"""Формирует Markdown-отчет о состоянии MEGA CODER.

Reporter удобно запускать как Kubernetes CronJob или вручную перед защитой:
он читает pods/deployments/events из Kubernetes API, опционально проверяет
Prometheus/Loki, печатает Markdown в stdout и может отправить краткую сводку
в alert-bot webhook.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import httpx


REPORT_NAMESPACE = os.getenv("REPORT_NAMESPACE", "mega-coder")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://monitoring-kube-prometheus-prometheus.monitoring.svc:9090")
LOKI_URL = os.getenv("LOKI_URL", "http://loki.monitoring.svc:3100")
ALERT_BOT_REPORT_URL = os.getenv("ALERT_BOT_REPORT_URL", "")
ALERTMANAGER_WEBHOOK_SECRET = os.getenv("ALERTMANAGER_WEBHOOK_SECRET", "")
OUTPUT_PATH = os.getenv("REPORT_OUTPUT_PATH", "")
SEND_REPORT_TO_TELEGRAM = os.getenv("SEND_REPORT_TO_TELEGRAM", "false").lower() == "true"


def now_utc() -> str:
    """Human-readable timestamp for report headers."""
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


class KubernetesApi:
    """Minimal in-cluster Kubernetes client without kubectl dependency."""

    def __init__(self) -> None:
        host = os.getenv("KUBERNETES_SERVICE_HOST")
        port = os.getenv("KUBERNETES_SERVICE_PORT", "443")
        self.base_url = f"https://{host}:{port}" if host else ""
        self.token_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
        self.ca_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")

    def enabled(self) -> bool:
        """Local runs without a cluster should produce a clear report, not crash."""
        return bool(self.base_url and self.token_path.exists())

    def get(self, path: str) -> dict[str, Any]:
        """Calls Kubernetes API with the pod service-account token."""
        if not self.enabled():
            return {"items": [], "warning": "Kubernetes API is not available in local mode"}
        token = self.token_path.read_text(encoding="utf-8").strip()
        verify: str | bool = str(self.ca_path) if self.ca_path.exists() else False
        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(timeout=10, verify=verify) as client:
            response = client.get(f"{self.base_url}{path}", headers=headers)
            response.raise_for_status()
            return response.json()


def prometheus_query(query: str) -> str:
    """Runs a Prometheus instant query; returns '-' if Prometheus is not reachable."""
    if not PROMETHEUS_URL:
        return "-"
    try:
        response = httpx.get(f"{PROMETHEUS_URL.rstrip('/')}/api/v1/query", params={"query": query}, timeout=8)
        response.raise_for_status()
        result = response.json().get("data", {}).get("result", [])
        if not result:
            return "no data"
        # Для защиты важны человекочитаемые имена: deployment -> pod -> instance.
        return ", ".join(
            f"{item.get('metric', {}).get('deployment') or item.get('metric', {}).get('pod') or item.get('metric', {}).get('instance', 'value')}: {item.get('value', ['-', '-'])[1]}"
            for item in result[:5]
        )
    except Exception as exc:  # noqa: BLE001 - report should stay resilient.
        return f"unavailable: {exc}"


def loki_errors() -> str:
    """Samples Loki logs for ERROR lines; keeps failure non-fatal for demo stability."""
    if not LOKI_URL:
        return "-"
    # Не включаем reporter/тестовые job logs, чтобы отчет показывал ошибки приложения.
    query = f'{{namespace="{REPORT_NAMESPACE}", pod=~"mega-mega-coder-(api|web|worker).*"}} |= "ERROR"'
    try:
        response = httpx.get(
            f"{LOKI_URL.rstrip('/')}/loki/api/v1/query_range",
            params={"query": query, "limit": 5, "direction": "BACKWARD"},
            timeout=8,
        )
        response.raise_for_status()
        streams = response.json().get("data", {}).get("result", [])
        lines: list[str] = []
        for stream in streams:
            for _, line in stream.get("values", [])[:5]:
                lines.append(line[:220])
        return "\n".join(f"- `{line}`" for line in lines) if lines else "no recent ERROR logs"
    except Exception as exc:  # noqa: BLE001
        return f"unavailable: {exc}"


def summarize_pods(pods: list[dict[str, Any]]) -> tuple[list[str], int]:
    """Builds a table with pod phase/readiness/restarts."""
    rows = ["| Pod | Фаза | Готовность | Перезапуски |", "|---|---|---:|---:|"]
    total_restarts = 0
    for pod in pods:
        name = pod.get("metadata", {}).get("name", "-")
        phase = pod.get("status", {}).get("phase", "-")
        statuses = pod.get("status", {}).get("containerStatuses", []) or []
        ready = sum(1 for item in statuses if item.get("ready"))
        restarts = sum(int(item.get("restartCount", 0)) for item in statuses)
        total_restarts += restarts
        rows.append(f"| `{name}` | {phase} | {ready}/{len(statuses)} | {restarts} |")
    return rows, total_restarts


def summarize_deployments(deployments: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Builds a deployment table and returns unavailable deployment names."""
    rows = ["| Deployment | Желаемые реплики | Доступные реплики | Недоступно |", "|---|---:|---:|---:|"]
    unavailable: list[str] = []
    for dep in deployments:
        name = dep.get("metadata", {}).get("name", "-")
        desired = dep.get("spec", {}).get("replicas", 0)
        available = dep.get("status", {}).get("availableReplicas", 0)
        missing = max(int(desired or 0) - int(available or 0), 0)
        if missing:
            unavailable.append(name)
        rows.append(f"| `{name}` | {desired} | {available} | {missing} |")
    return rows, unavailable


def event_timestamp(event: dict[str, Any]) -> str:
    """Normalizes event time: Kubernetes may return null for older event fields."""
    return str(event.get("lastTimestamp") or event.get("eventTime") or event.get("metadata", {}).get("creationTimestamp") or "")


def build_report() -> str:
    """Collects all sources and returns final Markdown report text."""
    k8s = KubernetesApi()
    pods = k8s.get(f"/api/v1/namespaces/{REPORT_NAMESPACE}/pods").get("items", [])
    deployments = k8s.get(f"/apis/apps/v1/namespaces/{REPORT_NAMESPACE}/deployments").get("items", [])
    events = k8s.get(f"/api/v1/namespaces/{REPORT_NAMESPACE}/events").get("items", [])

    pod_rows, restart_count = summarize_pods(pods)
    deployment_rows, unavailable = summarize_deployments(deployments)
    warning_events = [
        f"- `{event.get('reason', '-')}` {event.get('message', '-')[:220]}"
        for event in sorted(events, key=event_timestamp, reverse=True)
        if event.get("type") in {"Warning", "Error"}
    ][:10]

    cpu_summary = prometheus_query(f'sum(rate(container_cpu_usage_seconds_total{{namespace="{REPORT_NAMESPACE}",container!="",pod!=""}}[5m])) by (pod)')
    memory_summary = prometheus_query(f'sum(container_memory_working_set_bytes{{namespace="{REPORT_NAMESPACE}",container!="",pod!=""}}) by (pod)')
    availability = prometheus_query(f'kube_deployment_status_replicas_available{{namespace="{REPORT_NAMESPACE}"}}')

    sections = [
        "# MEGA CODER: отчет по Kubernetes",
        "",
        f"- Сформирован: `{now_utc()}`",
        f"- Namespace: `{REPORT_NAMESPACE}`",
        f"- Pod'ов: `{len(pods)}`",
        f"- Перезапусков контейнеров всего: `{restart_count}`",
        f"- Deployment без нужного числа реплик: `{', '.join(unavailable) if unavailable else 'нет'}`",
        "",
        "## Pods",
        *pod_rows,
        "",
        "## Deployments",
        *deployment_rows,
        "",
        "## Последние Kubernetes Warning/Error events",
        "_Это диагностические события Kubernetes; они могут быть историческими и не всегда означают текущую аварию._",
        *(warning_events or ["- свежих Warning/Error events нет"]),
        "",
        "## Краткая сводка метрик",
        f"- CPU по pod'ам: `{cpu_summary}`",
        f"- Память по pod'ам: `{memory_summary}`",
        f"- Доступные реплики: `{availability}`",
        "",
        "## Пример ERROR-логов из Loki",
        loki_errors(),
        "",
        "## Сводка по приложению",
        "- `api`, `web`, `worker` должны иметь по 2 реплики.",
        "- `redis` должен иметь 1 реплику.",
        "- Alerting построен через Prometheus rules + Alertmanager webhook + Telegram bridge.",
        "",
    ]
    return "\n".join(sections)


def send_report(report: str) -> None:
    """Posts the report to alert-bot, which keeps Telegram formatting in one service."""
    if not SEND_REPORT_TO_TELEGRAM or not ALERT_BOT_REPORT_URL:
        return
    headers = {"X-Webhook-Secret": ALERTMANAGER_WEBHOOK_SECRET} if ALERTMANAGER_WEBHOOK_SECRET else {}
    response = httpx.post(ALERT_BOT_REPORT_URL, json={"title": "MEGA CODER: отчет по Kubernetes", "text": report[:3000]}, headers=headers, timeout=10)
    response.raise_for_status()


def main() -> int:
    """CLI entrypoint used by the Kubernetes CronJob."""
    report = build_report()
    print(report)
    if OUTPUT_PATH:
        Path(OUTPUT_PATH).write_text(report, encoding="utf-8")
    send_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
