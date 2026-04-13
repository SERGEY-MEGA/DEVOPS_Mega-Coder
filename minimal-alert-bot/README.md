# minimal-alert-bot

Изолированный минимум: **POST /webhook** (простой JSON или **Alertmanager**), **POST /gitlab-webhook** (GitLab). Не связан с Helm, CI и основным `services/alert-bot`.

- Простой тест `{"status","alertname"}` — **одна строка** без HTML: **`СРАБАТЫВАЕТ TestAlert`** (статусы по-русски).
- Payload с **`alerts[].labels`** — развёрнутое сообщение (HTML): группа, **СРАБАТЫВАЕТ / ВОССТАНОВЛЕНО**, серьёзность, неймспейс, под/деплой, кратко, описание, начало.

На macOS используй **`python3`** и **`pip3`** (команды `python` / `pip` часто отсутствуют).

## Важно про 404 от Telegram

- URL всегда **`https://api.telegram.org/bot<ТОКЕН>/...`** — слово **`bot`** перед токеном обязательно.  
- Если в `export` стоит фраза вроде **`НОВЫЙ_ТОКЕН_ОТ_BOTFATHER`** (из примера в чате) — это **не** токен, будет **404**. Нужна строка вида **`123456789:AAH...`** из BotFather.

## Вариант A: файл `.env` (удобно, не светить токен в истории команд)

```bash
cd minimal-alert-bot
cp .env.example .env
# Открой .env в редакторе и вставь TELEGRAM_BOT_TOKEN=... и TELEGRAM_CHAT_ID=...
chmod +x direct_ping.sh run.sh
./direct_ping.sh "СРАБАТЫВАЕТ TestAlert"
```

Ожидается JSON с `"ok":true` и сообщение в Telegram.

## Вариант B: только `export`

```bash
cd minimal-alert-bot
export TELEGRAM_BOT_TOKEN="реальный_токен_от_BotFather"
export TELEGRAM_CHAT_ID="337328161"
./direct_ping.sh "СРАБАТЫВАЕТ TestAlert"
```

## Запуск webhook-сервера (локально)

```bash
cd minimal-alert-bot
python3 -m venv .venv && source .venv/bin/activate   # опционально
pip3 install -r requirements.txt
# либо .env как выше, либо export
chmod +x run.sh
./run.sh
```

Сервис слушает `http://0.0.0.0:8080`.

## Тесты

### 1) Простой алерт (как раньше, plain text)

```bash
curl -sS -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"status":"firing","alertname":"TestAlert"}'
```

**Сообщение в Telegram:** `СРАБАТЫВАЕТ TestAlert` (без разметки).

### 2) Alertmanager webhook (группа + поля)

Из **корня репозитория** (`examples/...`):

```bash
curl -sS -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  --data-binary @examples/alertmanager-firing.json
```

Если ты уже в `minimal-alert-bot/`, путь к примеру: `../examples/alertmanager-firing.json`.

Для **resolved**:

```bash
curl -sS -X POST http://127.0.0.1:8080/webhook \
  -H "Content-Type: application/json" \
  --data-binary @examples/alertmanager-resolved.json
```

**Пример итога в Telegram (смысл, интерфейс на русском):**

```text
🔴 Alertmanager: СРАБАТЫВАЕТ
алертов в группе: 1
метки группы: {"alertname": "PodCrashLooping", "severity": "critical"}
общие метки: { ... }

🔴 СРАБАТЫВАЕТ · PodCrashLooping
серьёзность: critical (критично)
неймспейс: mega-coder
под / деплой / сервис: mega-mega-coder-api-demo
кратко: Pod находится в CrashLoopBackOff
описание: Тестовый pod постоянно перезапускается...
начало: 2026-04-13T13:00:00Z
ранбук: RUNBOOKS.md#podcrashlooping
```

(Имена алертов и значения из Prometheus остаются как в данных; подписи полей — по-русски, включён HTML.)

### 3) GitLab webhook

```bash
curl -sS -X POST http://127.0.0.1:8080/gitlab-webhook \
  -H "Content-Type: application/json" \
  -H "X-Gitlab-Event: Pipeline Hook" \
  --data-binary @examples/gitlab-pipeline-failed.json
```

Push (пример тела можно собрать вручную или взять из документации GitLab):

```bash
curl -sS -X POST http://127.0.0.1:8080/gitlab-webhook \
  -H "Content-Type: application/json" \
  -H "X-Gitlab-Event: Push Hook" \
  -d '{"object_kind":"push","user":{"name":"Sergey Mega"},"project":{"path_with_namespace":"MEGA/deveps-mega-coder"},"ref":"refs/heads/main","commits":[]}'
```

**Пример итога (pipeline failed):**

```text
🔴 GitLab — pipeline: ОШИБКА
проект: MEGA/deveps-mega-coder
ветка: main
коммит: 76475c5fa36d
пользователь: Sergey Mega
ссылка: https://gitlub.ru/MEGA/deveps-mega-coder/-/pipelines/23
```

## Docker

```bash
cd minimal-alert-bot
docker build -t minimal-alert-bot:local .
docker run --rm -p 8080:8080 \
  -e TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  -e TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
  minimal-alert-bot:local
```

Переменные задай через `-e` или `.env`. Файл `.env` в репозиторий не коммитится.
