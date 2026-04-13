#!/usr/bin/env python3
"""Минимум: POST /webhook (Alertmanager + простой JSON) → Telegram. POST /gitlab-webhook → Telegram."""

from __future__ import annotations

import json
import logging
import os
import sys
from html import escape
from typing import Any

import requests
from flask import Flask, request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("minimal-alert-bot")

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def h(value: Any) -> str:
    """HTML для Telegram parse_mode."""
    if value is None:
        return "-"
    return escape(str(value), quote=False)


def status_ru(status: str | None) -> str:
    """FIRING/RESOLVED → русские заголовки для демонстрации."""
    s = (status or "").strip().lower()
    return {
        "firing": "СРАБАТЫВАЕТ",
        "resolved": "ВОССТАНОВЛЕНО",
        "pending": "ОЖИДАНИЕ",
        "inactive": "НЕАКТИВЕН",
        "unknown": "НЕИЗВЕСТНО",
    }.get(s, (status or "?").upper())


def severity_ru(sev: str | None) -> str:
    s = (sev or "-").strip().lower()
    ru = {
        "critical": "критично",
        "warning": "предупреждение",
        "info": "информация",
        "none": "нет",
    }.get(s)
    if sev in (None, "", "-"):
        return "-"
    if ru:
        return f"{sev} ({ru})"
    return str(sev)


def pipeline_status_ru(st: str | None) -> str:
    s = (st or "-").strip().lower()
    return {
        "failed": "ОШИБКА",
        "success": "УСПЕХ",
        "running": "ВЫПОЛНЯЕТСЯ",
        "pending": "ОЖИДАНИЕ",
        "canceled": "ОТМЕНЁН",
        "cancelled": "ОТМЕНЁН",
        "skipped": "ПРОПУЩЕН",
        "created": "СОЗДАН",
        "manual": "ВРУЧНУЮ",
    }.get(s, (st or "-").upper())


def pick_object(labels: dict[str, Any]) -> str:
    for key in ("pod", "deployment", "service", "job", "daemonset", "statefulset", "instance"):
        if labels.get(key):
            return str(labels[key])
    return "-"


def split_telegram_html(text: str, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    cur: list[str] = []
    n = 0
    for line in text.splitlines():
        line_len = len(line) + 1
        if n + line_len > limit and cur:
            chunks.append("\n".join(cur))
            cur = []
            n = 0
        cur.append(line)
        n += line_len
    if cur:
        chunks.append("\n".join(cur))
    return chunks


def send_telegram(text: str, *, parse_mode: str | None = None) -> dict:
    if not TOKEN or not CHAT_ID:
        raise RuntimeError("Задайте TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    last: dict = {}
    for chunk in split_telegram_html(text) if parse_mode == "HTML" else ([text] if len(text) <= 4096 else split_telegram_html(text, 4090)):
        payload: dict[str, Any] = {"chat_id": CHAT_ID, "text": chunk}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        log.info("Telegram request chat_id=%s parse_mode=%s chars=%s", CHAT_ID, parse_mode, len(chunk))
        r = requests.post(url, json=payload, timeout=25)
        log.info("Telegram HTTP %s body=%s", r.status_code, r.text[:500])
        r.raise_for_status()
        last = r.json()
    return last


def is_rich_alertmanager_shape(data: dict[str, Any]) -> bool:
    """Полноценный или частичный payload Alertmanager: есть alerts с labels."""
    alerts = data.get("alerts")
    if not isinstance(alerts, list) or not alerts:
        return False
    first = alerts[0]
    return isinstance(first, dict) and isinstance(first.get("labels"), dict)


def format_alertmanager_telegram(data: dict[str, Any]) -> str:
    """Группа + каждый алерт: статусы и подписи полей на русском."""
    raw_group = (data.get("status") or "firing").lower()
    alerts = data.get("alerts") or []
    group_labels = data.get("groupLabels") or {}
    common = data.get("commonLabels") or {}

    icon = "🟢" if raw_group == "resolved" else "🔴"
    header = [
        f"{icon} <b>Alertmanager: {h(status_ru(raw_group))}</b>",
        f"алертов в группе: <b>{len(alerts)}</b>",
        f"метки группы: <code>{h(json.dumps(group_labels, ensure_ascii=False))}</code>",
    ]
    if common:
        header.append(f"общие метки: <code>{h(json.dumps(common, ensure_ascii=False))}</code>")

    blocks: list[str] = []
    for alert in alerts:
        if not isinstance(alert, dict):
            continue
        labels = alert.get("labels") or {}
        annotations = alert.get("annotations") or {}
        raw_st = (alert.get("status") or data.get("status") or "firing").lower()
        st_display = status_ru(raw_st)
        name = labels.get("alertname", "Alert")
        severity = severity_ru(labels.get("severity"))
        ns = labels.get("namespace", "-")
        obj = pick_object(labels)
        summary = annotations.get("summary", "-")
        desc = annotations.get("description", "-")
        starts = alert.get("startsAt", "-")
        ends = alert.get("endsAt")
        runbook = annotations.get("runbook_url")

        sub_icon = "🟢" if raw_st == "resolved" else "🔴"
        lines = [
            f"{sub_icon} <b>{h(st_display)}</b> · <b>{h(name)}</b>",
            f"серьёзность: <code>{h(severity)}</code>",
            f"неймспейс: <code>{h(ns)}</code>",
            f"под / деплой / сервис: <code>{h(obj)}</code>",
            f"кратко: {h(summary)}",
            f"описание: {h(desc)}",
            f"начало: <code>{h(starts)}</code>",
        ]
        if ends:
            lines.append(f"окончание: <code>{h(ends)}</code>")
        if runbook:
            lines.append(f"ранбук: {h(runbook)}")
        blocks.append("\n".join(lines))

    body = "\n\n—\n\n".join(blocks) if blocks else "Нет алертов в списке <code>alerts</code>"
    return "\n".join(header) + "\n\n" + body


def format_alert_text(data: dict | list | None) -> str:
    """Простой JSON без массива alerts: одна строка, статус по-русски."""
    if data is None:
        return "СРАБАТЫВАЕТ TestAlert"
    if isinstance(data, list):
        data = data[0] if data else {}
    if not isinstance(data, dict):
        return "СРАБАТЫВАЕТ TestAlert"

    if data.get("text"):
        return str(data["text"])

    if is_rich_alertmanager_shape(data):
        # не должны сюда попадать
        return format_alertmanager_telegram(data)

    name = data.get("alertname", "TestAlert")
    raw = (data.get("status") or "firing").lower()
    return f"{status_ru(raw)} {name}"


def format_gitlab_telegram(payload: dict[str, Any], event_header: str) -> str:
    """Pipeline, push, merge_request — читаемый HTML."""
    project = payload.get("project") or {}
    project_path = project.get("path_with_namespace") or project.get("web_url") or "-"
    user = payload.get("user_name") or (payload.get("user") or {}).get("name") or "-"
    obj = payload.get("object_attributes") or {}
    kind = payload.get("object_kind") or event_header.replace(" Hook", "").replace(" ", "_").lower()

    if kind == "pipeline" or event_header == "Pipeline Hook":
        status = str(obj.get("status", "-"))
        emoji = "🔴" if status == "failed" else "🟢" if status == "success" else "🔵"
        st_ru = pipeline_status_ru(status)
        return "\n".join(
            [
                f"{emoji} <b>GitLab — pipeline: {h(st_ru)}</b>",
                f"проект: <code>{h(project_path)}</code>",
                f"ветка: <code>{h(obj.get('ref', '-'))}</code>",
                f"коммит: <code>{h(str(obj.get('sha', '-'))[:12])}</code>",
                f"пользователь: {h(user)}",
                f"ссылка: {h(obj.get('url', '-'))}",
            ]
        )

    if kind in ("push", "tag_push") or event_header in ("Push Hook", "Tag Push Hook"):
        commits = payload.get("commits") or []
        return "\n".join(
            [
                "🧩 <b>GitLab — отправка в репозиторий (push)</b>",
                f"проект: <code>{h(project_path)}</code>",
                f"ссылка на ref: <code>{h(payload.get('ref', '-'))}</code>",
                f"пользователь: {h(user)}",
                f"коммитов: <b>{len(commits)}</b>",
            ]
        )

    if kind == "merge_request" or event_header == "Merge Request Hook":
        return "\n".join(
            [
                "🔀 <b>GitLab — запрос на слияние (merge request)</b>",
                f"проект: <code>{h(project_path)}</code>",
                f"заголовок: {h(obj.get('title', '-'))}",
                f"состояние: <code>{h(obj.get('state', '-'))}</code>",
                f"ветки: {h(obj.get('source_branch', '-'))} → {h(obj.get('target_branch', '-'))}",
                f"ссылка: {h(obj.get('url', '-'))}",
            ]
        )

    return "\n".join(
        [
            "ℹ️ <b>GitLab</b>",
            f"событие: <code>{h(event_header or kind)}</code>",
            f"проект: <code>{h(project_path)}</code>",
            f"пользователь: {h(user)}",
        ]
    )


@app.get("/health")
def health():
    return {
        "ok": True,
        "telegram_configured": bool(TOKEN and CHAT_ID),
        "endpoints": ["POST /webhook", "POST /gitlab-webhook"],
    }


@app.post("/webhook")
def webhook():
    raw = request.get_data(as_text=True)
    log.info("POST /webhook raw_len=%s", len(raw or ""))
    try:
        data = request.get_json(force=True, silent=False)
    except Exception as exc:  # noqa: BLE001
        log.warning("JSON parse error: %s raw=%s", exc, raw[:2000])
        return {"ok": False, "error": "invalid json"}, 400

    if not isinstance(data, dict):
        return {"ok": False, "error": "json must be an object"}, 400

    log.info("POST /webhook json=%s", json.dumps(data, ensure_ascii=False)[:4000])

    if is_rich_alertmanager_shape(data):
        text = format_alertmanager_telegram(data)
        parse_mode = "HTML"
    else:
        text = format_alert_text(data)
        parse_mode = None

    try:
        tg = send_telegram(text, parse_mode=parse_mode)
    except Exception as exc:  # noqa: BLE001
        log.exception("Telegram failed: %s", exc)
        return {"ok": False, "error": str(exc), "would_send": text}, 502

    log.info("Sent OK (%s)", "HTML" if parse_mode else "plain")
    return {"ok": True, "sent": text, "parse_mode": parse_mode, "telegram": tg}


@app.post("/gitlab-webhook")
def gitlab_webhook():
    raw = request.get_data(as_text=True)
    event = request.headers.get("X-Gitlab-Event", "") or ""
    log.info("POST /gitlab-webhook event=%s raw_len=%s", event, len(raw or ""))
    try:
        data = request.get_json(force=True, silent=False)
    except Exception as exc:  # noqa: BLE001
        log.warning("JSON parse error: %s", exc)
        return {"ok": False, "error": "invalid json"}, 400

    if not isinstance(data, dict):
        return {"ok": False, "error": "json must be an object"}, 400

    log.info("POST /gitlab-webhook json=%s", json.dumps(data, ensure_ascii=False)[:3000])

    text = format_gitlab_telegram(data, event)
    try:
        tg = send_telegram(text, parse_mode="HTML")
    except Exception as exc:  # noqa: BLE001
        log.exception("Telegram failed: %s", exc)
        return {"ok": False, "error": str(exc), "would_send": text}, 502

    return {"ok": True, "sent": text, "event": event, "telegram": tg}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    log.info("Listening on 0.0.0.0:%s POST /webhook POST /gitlab-webhook", port)
    app.run(host="0.0.0.0", port=port, debug=False)
