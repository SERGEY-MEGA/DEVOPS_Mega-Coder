"""Webhook bridge: Alertmanager/Grafana/GitLab -> Telegram.

Файл специально написан без "магии": каждый endpoint принимает один тип события,
нормализует payload в человекочитаемый текст и отправляет его в Telegram.
Секреты берутся только из env/Kubernetes Secret, поэтому токены не попадают в git.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from html import escape
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Request


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("mega-coder-alert-bot")
# httpx на INFO пишет полный URL запроса. Для Telegram это содержит bot token,
# поэтому внешний transport-лог оставляем только на WARNING и выше.
logging.getLogger("httpx").setLevel(logging.WARNING)

app = FastAPI(
    title="MEGA CODER Alert Bot",
    description="Receives Alertmanager/Grafana/GitLab webhooks and sends Telegram notifications.",
    version="1.0.0",
)


def env(name: str, default: str = "") -> str:
    """Small helper: centralizes env reading and keeps defaults visible."""
    return os.getenv(name, default).strip()


TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")
TELEGRAM_PARSE_MODE = env("TELEGRAM_PARSE_MODE", "HTML")
TELEGRAM_ENABLE_COMMANDS = env("TELEGRAM_ENABLE_COMMANDS", "false").lower() == "true"
ALERTMANAGER_WEBHOOK_SECRET = env("ALERTMANAGER_WEBHOOK_SECRET")
GITLAB_WEBHOOK_SECRET = env("GITLAB_WEBHOOK_SECRET")
APP_ENV = env("APP_ENV", "dev")
CLUSTER_NAME = env("CLUSTER_NAME", "k3s-home")
SEND_TIMEOUT_SECONDS = float(env("SEND_TIMEOUT_SECONDS", "8"))
SEND_RETRIES = int(env("SEND_RETRIES", "3"))
STATUS_CHECK_URLS = env(
    "STATUS_CHECK_URLS",
    "Приложение=http://127.0.0.1:30080/;API=http://127.0.0.1:30080/api/info;Grafana=http://127.0.0.1:30030/login;GitLab=http://127.0.0.1:8080/users/sign_in",
)

telegram_polling_task: asyncio.Task[None] | None = None


def require_secret(expected: str, actual: str | None, source: str) -> None:
    """Protects webhook endpoints when a secret is configured.

    If the secret env var is empty, demo mode is allowed. This keeps the chart
    deployable before the student creates a real Telegram bot secret.
    """
    if expected and actual != expected:
        logger.warning("Rejected %s webhook: invalid secret", source)
        raise HTTPException(status_code=401, detail=f"Invalid {source} webhook secret")


def html(value: Any) -> str:
    """Telegram HTML parse_mode requires escaping user-controlled payload fields."""
    if value is None:
        return "-"
    return escape(str(value), quote=False)


def severity_icon(status: str, severity: str) -> str:
    """Maps alert status/severity to a visual signal that is easy to scan."""
    if status == "resolved":
        return "🟢"
    if severity == "critical":
        return "🔴"
    if severity == "warning":
        return "🟡"
    return "🔵"


def status_ru(status: str) -> str:
    """Returns a Russian status label for Telegram messages shown on defense."""
    return {
        "firing": "СРАБАТЫВАЕТ",
        "resolved": "ВОССТАНОВЛЕНО",
        "success": "УСПЕХ",
        "failed": "ОШИБКА",
    }.get(status.lower(), status.upper())


def severity_ru(severity: str) -> str:
    """Keeps severity recognizable while adding a Russian explanation."""
    return {
        "critical": "critical / критично",
        "warning": "warning / предупреждение",
        "info": "info / информация",
    }.get(severity.lower(), severity)


def pick_label(labels: dict[str, Any], *names: str) -> str:
    """Returns the first useful Kubernetes/GitLab label from a payload."""
    for name in names:
        if labels.get(name):
            return str(labels[name])
    return "-"


def split_telegram_message(text: str, limit: int = 3900) -> list[str]:
    """Telegram has a 4096 character limit; keep a safety margin for HTML tags."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in text.splitlines():
        if current_len + len(line) + 1 > limit and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


async def send_telegram_to(chat_id: str, text: str) -> dict[str, Any]:
    """Sends a Telegram message to a concrete chat with retry/timeout."""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        logger.warning("Telegram token/chat_id are not configured; notification skipped")
        return {"sent": False, "reason": "telegram_not_configured"}

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload_base = {
        "chat_id": chat_id,
        "parse_mode": TELEGRAM_PARSE_MODE,
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient(timeout=SEND_TIMEOUT_SECONDS) as client:
        for chunk in split_telegram_message(text):
            last_error: str | None = None
            for attempt in range(1, SEND_RETRIES + 1):
                try:
                    response = await client.post(url, json={**payload_base, "text": chunk})
                    response.raise_for_status()
                    logger.info("Telegram notification sent, chars=%s", len(chunk))
                    break
                except httpx.HTTPError as exc:
                    last_error = str(exc)
                    logger.warning("Telegram send failed attempt=%s error=%s", attempt, exc)
                    await asyncio.sleep(min(attempt, 3))
            else:
                raise HTTPException(status_code=502, detail=f"Telegram send failed: {last_error}")
    return {"sent": True}


async def send_telegram(text: str) -> dict[str, Any]:
    """Sends a message to the main configured Telegram chat."""
    return await send_telegram_to(TELEGRAM_CHAT_ID, text)


def status_targets() -> list[tuple[str, str]]:
    """Parses lightweight HTTP checks for the interactive /status command."""
    targets: list[tuple[str, str]] = []
    for item in STATUS_CHECK_URLS.split(";"):
        if not item.strip():
            continue
        name, _, url = item.partition("=")
        if name.strip() and url.strip():
            targets.append((name.strip(), url.strip()))
    return targets


async def build_status_message() -> str:
    """Builds a small Russian status report without heavy Kubernetes polling."""
    lines = [
        "📊 <b>MEGA CODER: статус стенда</b>",
        f"кластер: <code>{html(CLUSTER_NAME)}</code>",
        f"окружение: <code>{html(APP_ENV)}</code>",
        f"alert-bot: <code>Running</code>",
        "",
        "<b>HTTP-проверки:</b>",
    ]
    async with httpx.AsyncClient(timeout=5, follow_redirects=False) as client:
        for name, url in status_targets():
            try:
                response = await client.get(url)
                ok = 200 <= response.status_code < 400
                icon = "✅" if ok else "⚠️"
                lines.append(f"{icon} {html(name)}: <code>HTTP {response.status_code}</code>")
            except Exception as exc:  # noqa: BLE001 - status command should never crash polling.
                lines.append(f"🔴 {html(name)}: <code>{html(type(exc).__name__)}</code>")
    lines.extend(
        [
            "",
            "Команды: <code>/status</code>, <code>/help</code>",
        ]
    )
    return "\n".join(lines)


async def handle_telegram_command(message: dict[str, Any]) -> None:
    """Handles a single Telegram message from getUpdates polling."""
    chat = message.get("chat", {}) or {}
    chat_id = str(chat.get("id", ""))
    text = str(message.get("text", "")).strip()
    if not chat_id or not text:
        return
    if TELEGRAM_CHAT_ID and chat_id != TELEGRAM_CHAT_ID:
        logger.warning("Ignoring Telegram command from unexpected chat")
        return
    command = text.split()[0].split("@", 1)[0].lower()
    if command in {"/start", "/help"}:
        await send_telegram_to(
            chat_id,
            "👋 <b>MEGA CODER Alert Bot</b>\n\n"
            "Я отправляю alert'ы из Alertmanager/GitLab и могу ответить на команду <code>/status</code>.\n"
            "Секреты хранятся в Kubernetes Secret, в git они не попадают.",
        )
    elif command == "/status":
        await send_telegram_to(chat_id, await build_status_message())


async def telegram_command_polling() -> None:
    """Optional getUpdates loop for /status; disabled by default in Helm values."""
    if not TELEGRAM_ENABLE_COMMANDS:
        return
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram command polling disabled: token/chat_id are missing")
        return
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    offset = 0
    async with httpx.AsyncClient(timeout=35) as client:
        try:
            response = await client.get(f"{base_url}/getUpdates", params={"timeout": 0, "limit": 100})
            response.raise_for_status()
            updates = response.json().get("result", [])
            if updates:
                offset = max(int(update["update_id"]) for update in updates) + 1
        except httpx.HTTPError as exc:
            logger.warning("Telegram polling warmup failed: %s", exc)
        logger.info("Telegram command polling enabled")
        while True:
            try:
                response = await client.get(f"{base_url}/getUpdates", params={"timeout": 25, "offset": offset})
                response.raise_for_status()
                for update in response.json().get("result", []):
                    offset = int(update["update_id"]) + 1
                    if "message" in update:
                        await handle_telegram_command(update["message"])
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - keep command bot alive after transient Telegram/network errors.
                logger.warning("Telegram polling error: %s", exc)
                await asyncio.sleep(5)


@app.on_event("startup")
async def startup() -> None:
    """Starts optional Telegram command polling after FastAPI is ready."""
    global telegram_polling_task
    if TELEGRAM_ENABLE_COMMANDS:
        telegram_polling_task = asyncio.create_task(telegram_command_polling())


@app.on_event("shutdown")
async def shutdown() -> None:
    """Stops the polling task cleanly during Kubernetes pod termination."""
    if telegram_polling_task:
        telegram_polling_task.cancel()
        try:
            await telegram_polling_task
        except asyncio.CancelledError:
            pass


def format_alert(alert: dict[str, Any], default_status: str) -> str:
    """Formats one Alertmanager alert into a compact Telegram block."""
    labels = alert.get("labels", {}) or {}
    annotations = alert.get("annotations", {}) or {}
    status = str(alert.get("status") or default_status or "firing").lower()
    severity = str(labels.get("severity", "info")).lower()
    icon = severity_icon(status, severity)

    lines = [
        f"{icon} <b>{html(status_ru(status))} {html(severity_ru(severity))}</b> — <b>{html(labels.get('alertname', 'Alert'))}</b>",
        f"namespace: <code>{html(pick_label(labels, 'namespace'))}</code>",
        f"объект: <code>{html(pick_label(labels, 'pod', 'deployment', 'service', 'instance'))}</code>",
        f"кластер / приложение / окружение: <code>{html(labels.get('cluster', CLUSTER_NAME))}</code> / <code>{html(labels.get('app', 'mega-coder'))}</code> / <code>{html(labels.get('env', APP_ENV))}</code>",
        f"кратко: {html(annotations.get('summary', '-'))}",
        f"описание: {html(annotations.get('description', '-'))}",
        f"начало: <code>{html(alert.get('startsAt', '-'))}</code>",
    ]
    if annotations.get("runbook_url"):
        lines.append(f"runbook: {html(annotations['runbook_url'])}")
    return "\n".join(lines)


def format_alertmanager(payload: dict[str, Any]) -> str:
    """Formats grouped Alertmanager webhook payload with all included alerts."""
    alerts = payload.get("alerts", []) or []
    status = str(payload.get("status", "firing")).lower()
    group_labels = payload.get("groupLabels", {}) or {}
    common_labels = payload.get("commonLabels", {}) or {}
    severity = str(common_labels.get("severity", "info")).lower()
    icon = severity_icon(status, severity)

    header = [
        f"{icon} <b>Alertmanager: {html(status_ru(status))}</b>",
        f"алертов в группе: <b>{len(alerts)}</b>",
        f"группа: <code>{html(json.dumps(group_labels, ensure_ascii=False))}</code>",
        f"кластер / окружение: <code>{html(common_labels.get('cluster', CLUSTER_NAME))}</code> / <code>{html(common_labels.get('env', APP_ENV))}</code>",
    ]
    body = ["\n\n".join(format_alert(alert, status) for alert in alerts)] if alerts else ["В payload нет alert-событий"]
    return "\n".join(header) + "\n\n" + "\n\n---\n\n".join(body)


def format_grafana(payload: dict[str, Any]) -> str:
    """Formats Grafana webhook alerts when Grafana Alerting is used as a fallback source."""
    title = payload.get("title") or payload.get("ruleName") or "Grafana alert"
    state = str(payload.get("state") or payload.get("status") or "firing").lower()
    message = payload.get("message") or payload.get("evalMatches") or "-"
    return "\n".join(
        [
            f"{severity_icon(state, 'warning')} <b>Grafana: {html(status_ru(state))}</b>",
            f"правило: <b>{html(title)}</b>",
            f"сообщение: {html(message)}",
            f"дашборд: {html(payload.get('dashboardURL', '-'))}",
            f"панель: {html(payload.get('panelURL', '-'))}",
        ]
    )


def format_gitlab(payload: dict[str, Any], event: str) -> str:
    """Formats common GitLab webhooks: push, pipeline, MR, tag/release."""
    project = payload.get("project", {}) or {}
    project_path = project.get("path_with_namespace") or project.get("web_url") or "-"
    user = payload.get("user_name") or payload.get("user", {}).get("name") or payload.get("user_username") or "-"
    object_attributes = payload.get("object_attributes", {}) or {}
    object_kind = payload.get("object_kind") or event or "gitlab_event"

    if object_kind == "pipeline":
        status = object_attributes.get("status", "-")
        emoji = "🔴" if status == "failed" else "🟢" if status == "success" else "🔵"
        return "\n".join(
            [
                f"{emoji} <b>GitLab pipeline: {html(status_ru(str(status)))}</b>",
                f"проект: <code>{html(project_path)}</code>",
                f"ветка/tag: <code>{html(object_attributes.get('ref', '-'))}</code>",
                f"commit: <code>{html(str(object_attributes.get('sha', '-'))[:8])}</code>",
                f"пользователь: {html(user)}",
                f"ссылка: {html(object_attributes.get('url', '-'))}",
            ]
        )

    if object_kind in {"push", "tag_push"}:
        commits = payload.get("commits", []) or []
        return "\n".join(
            [
                "🧩 <b>GitLab: push-событие</b>",
                f"проект: <code>{html(project_path)}</code>",
                f"ветка/tag: <code>{html(payload.get('ref', '-'))}</code>",
                f"пользователь: {html(user)}",
                f"коммитов: <b>{len(commits)}</b>",
                f"checkout_sha: <code>{html(str(payload.get('checkout_sha', '-'))[:8])}</code>",
            ]
        )

    if object_kind == "merge_request":
        return "\n".join(
            [
                "🔀 <b>GitLab: merge request</b>",
                f"проект: <code>{html(project_path)}</code>",
                f"заголовок: {html(object_attributes.get('title', '-'))}",
                f"статус: <code>{html(object_attributes.get('state', '-'))}</code>",
                f"source -> target: <code>{html(object_attributes.get('source_branch', '-'))}</code> → <code>{html(object_attributes.get('target_branch', '-'))}</code>",
                f"ссылка: {html(object_attributes.get('url', '-'))}",
            ]
        )

    if object_kind == "release":
        return "\n".join(
            [
                "🏷️ <b>GitLab: release-событие</b>",
                f"проект: <code>{html(project_path)}</code>",
                f"название: {html(payload.get('name', '-'))}",
                f"tag: <code>{html(payload.get('tag', '-'))}</code>",
                f"ссылка: {html(payload.get('url', '-'))}",
            ]
        )

    return "\n".join(
        [
            "ℹ️ <b>GitLab: событие</b>",
            f"тип: <code>{html(object_kind)}</code>",
            f"проект: <code>{html(project_path)}</code>",
            f"пользователь: {html(user)}",
        ]
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Kubernetes liveness/readiness endpoint."""
    return {"status": "ok"}


@app.post("/webhook/alertmanager")
async def alertmanager_webhook(
    request: Request,
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
) -> dict[str, Any]:
    """Main production path: Alertmanager grouped alerts -> Telegram."""
    require_secret(ALERTMANAGER_WEBHOOK_SECRET, x_webhook_secret, "alertmanager")
    payload = await request.json()
    message = format_alertmanager(payload)
    result = await send_telegram(message)
    return {"ok": True, "source": "alertmanager", **result}


@app.post("/webhook/grafana")
async def grafana_webhook(
    request: Request,
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
) -> dict[str, Any]:
    """Fallback source: Grafana Alerting can reuse the same Telegram bridge."""
    require_secret(ALERTMANAGER_WEBHOOK_SECRET, x_webhook_secret, "grafana")
    payload = await request.json()
    result = await send_telegram(format_grafana(payload))
    return {"ok": True, "source": "grafana", **result}


@app.post("/webhook/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_token: str | None = Header(default=None, alias="X-Gitlab-Token"),
    x_gitlab_event: str | None = Header(default=None, alias="X-Gitlab-Event"),
) -> dict[str, Any]:
    """GitLab events -> Telegram: push, pipeline, MR, tag/release."""
    require_secret(GITLAB_WEBHOOK_SECRET, x_gitlab_token, "gitlab")
    payload = await request.json()
    result = await send_telegram(format_gitlab(payload, x_gitlab_event or ""))
    return {"ok": True, "source": "gitlab", "event": x_gitlab_event, **result}


@app.post("/webhook/report")
async def report_webhook(
    request: Request,
    x_webhook_secret: str | None = Header(default=None, alias="X-Webhook-Secret"),
) -> dict[str, Any]:
    """Reporter can send prepared Markdown/plain text summaries through the same bot."""
    require_secret(ALERTMANAGER_WEBHOOK_SECRET, x_webhook_secret, "report")
    payload = await request.json()
    title = payload.get("title", "MEGA CODER: отчет")
    text = payload.get("text", json.dumps(payload, ensure_ascii=False, indent=2))
    result = await send_telegram(f"📋 <b>{html(title)}</b>\n\n<pre>{html(text)}</pre>")
    return {"ok": True, "source": "reporter", **result}
