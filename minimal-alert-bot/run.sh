#!/usr/bin/env bash
# Запуск Flask-приложения (python3). Подхватывает .env из этой папки.
set -euo pipefail
cd "$(dirname "$0")"
if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi
: "${TELEGRAM_BOT_TOKEN:?Нет TELEGRAM_BOT_TOKEN — export или создай .env из .env.example}"
: "${TELEGRAM_CHAT_ID:?Нет TELEGRAM_CHAT_ID}"
exec python3 app.py
