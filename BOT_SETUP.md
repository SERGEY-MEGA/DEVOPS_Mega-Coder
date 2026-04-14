# Telegram Bot Setup для MEGA CODER Alerting

## 1. Создать бота

1. Откройте Telegram и найдите `@BotFather`.
2. Отправьте `/newbot`.
3. Задайте имя, например `MEGA CODER Alerts`.
4. Задайте username, например `mega_coder_alerts_bot`.
5. BotFather выдаст token.

Важно: token не вставлять в репозиторий, README, отчёты или screenshots.

## 2. Получить chat_id

1. Напишите своему боту любое сообщение, например `start`.
2. Локально выполните:

```bash
export TELEGRAM_BOT_TOKEN='вставить_только_локально'
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
```

3. В JSON найдите `message.chat.id`.
4. Это значение используйте как `TELEGRAM_CHAT_ID`.

Для группы: добавьте бота в группу, отправьте сообщение в группу, повторите `getUpdates`; у групп chat_id часто отрицательный.

## 3. Создать Kubernetes Secret

```bash
kubectl create secret generic mega-coder-alerting-secret \
  -n mega-coder \
  --from-literal=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  --from-literal=TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
  --from-literal=TELEGRAM_PARSE_MODE="HTML" \
  --from-literal=ALERTMANAGER_WEBHOOK_SECRET="$ALERTMANAGER_WEBHOOK_SECRET" \
  --from-literal=GITLAB_WEBHOOK_SECRET="$GITLAB_WEBHOOK_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Если запускаете на вашем сервере через k3s:

```bash
sudo k3s kubectl create secret generic mega-coder-alerting-secret \
  -n mega-coder \
  --from-literal=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
  --from-literal=TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
  --from-literal=TELEGRAM_PARSE_MODE="HTML" \
  --from-literal=ALERTMANAGER_WEBHOOK_SECRET="$ALERTMANAGER_WEBHOOK_SECRET" \
  --from-literal=GITLAB_WEBHOOK_SECRET="$GITLAB_WEBHOOK_SECRET" \
  --dry-run=client -o yaml | sudo k3s kubectl apply -f -
```

## 4. Включить alerting в Helm

Alerting выключен по умолчанию. Включение вручную:

```bash
helm upgrade --install mega ./helm/mega-coder \
  -n mega-coder \
  -f helm/mega-coder/values.yaml \
  -f examples/values-alerting-enable.yaml
```

На k3s сервере:

```bash
sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm upgrade --install mega ./helm/mega-coder \
  -n mega-coder \
  -f helm/mega-coder/values.yaml \
  -f examples/values-alerting-enable.yaml
```

Примечание для текущего домашнего k3s-стенда: в `examples/values-alerting-enable.yaml` включён `alerting.alertBot.hostNetwork=true`. Это нужно только потому, что Telegram API доступен с самого хоста, но недоступен из обычной pod-сети. Основное приложение, GitLab, Grafana и monitoring это не меняет.

## 5. Проверить alert-bot

```bash
sudo k3s kubectl get deploy,svc,cronjob -n mega-coder | grep -E 'alert-bot|reporter'
sudo k3s kubectl logs -n mega-coder deploy/mega-mega-coder-alert-bot --tail=50
```

Port-forward для локального теста:

```bash
sudo k3s kubectl port-forward -n mega-coder svc/mega-mega-coder-alert-bot 8088:8088
```

Отправить тестовый alert:

```bash
python3 scripts/smoke_alert_bot.py \
  --url http://127.0.0.1:8088/webhook/alertmanager \
  --payload examples/alertmanager-firing.json \
  --secret "$ALERTMANAGER_WEBHOOK_SECRET"
```

## 6. Команды бота

На demo-стенде в `examples/values-alerting-enable.yaml` включен флаг:

```yaml
alerting:
  alertBot:
    enableCommands: true
```

После деплоя можно написать боту в Telegram:

```text
/help
/status
```

`/help` кратко объясняет назначение бота. `/status` делает легкие HTTP-проверки приложения, API, Grafana и GitLab и присылает ответ на русском языке. Бот отвечает только в `TELEGRAM_CHAT_ID`, который записан в Kubernetes Secret, чтобы посторонний чат не мог дергать статус стенда.
