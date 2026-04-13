#!/usr/bin/env bash
# Прямая проверка Telegram API без webhook. Секреты: export или файл .env (не в git).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$SCRIPT_DIR/.env"
  set +a
fi

: "${TELEGRAM_BOT_TOKEN:?Задайте TELEGRAM_BOT_TOKEN (export или .env рядом со скриптом)}"
: "${TELEGRAM_CHAT_ID:?Задайте TELEGRAM_CHAT_ID}"

# Частая ошибка: скопирован текст-заглушка из инструкции вместо токена от BotFather → Telegram отвечает 404.
if [[ "$TELEGRAM_BOT_TOKEN" == *"НОВЫЙ"* ]] || [[ "$TELEGRAM_BOT_TOKEN" == *"BOTFATHER"* ]] || [[ "$TELEGRAM_BOT_TOKEN" == "ВАШ_"* ]]; then
  echo "Ошибка: TELEGRAM_BOT_TOKEN похож на заглушку из README, а не на реальный токен (формат: 123456789:AAH...)." >&2
  echo "Подставь свой текущий токен: export TELEGRAM_BOT_TOKEN='...' или положи его в minimal-alert-bot/.env" >&2
  exit 1
fi

MSG="${1:-СРАБАТЫВАЕТ TestAlert — прямой ping Telegram API}"
# Обязательный префикс bot в URL (без него будет 404).
curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${MSG}"

echo ""
