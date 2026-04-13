# Setup log: Telegram Alerting для MEGA CODER

## 1. Изучена существующая структура

В проекте уже были:

- Kubernetes/k3s live-стенд;
- Helm chart `helm/mega-coder`;
- monitoring stack: Prometheus, Grafana, Loki, Promtail, Node Exporter, kube-state-metrics;
- GitLab CI/CD через Kaniko и Helm deploy;
- документация `README.md`, `REPORT.md`, `PROJECT_MAP.md`.

## 2. Добавлен alert-bot

Создан сервис `services/alert-bot`:

- runtime: Python FastAPI;
- endpoints:
  - `/health`;
  - `/webhook/alertmanager`;
  - `/webhook/grafana`;
  - `/webhook/gitlab`;
  - `/webhook/report`;
- HTML escaping для Telegram;
- retry/timeout при отправке сообщений;
- поддержка severity `critical`, `warning`, `info`;
- поддержка статусов `firing` и `resolved`;
- секреты только через env/Kubernetes Secret.

## 3. Добавлен reporter

Создан сервис `services/reporter`:

- запускается как Kubernetes CronJob;
- использует in-cluster Kubernetes API, а не `kubectl`;
- собирает pods, restarts, deployments, warning/error events;
- опционально читает Prometheus и Loki;
- печатает Markdown-отчёт в stdout;
- может отправить краткую версию в Telegram через alert-bot.

## 4. Расширен Helm chart

Добавлены templates:

- `deployment-alert-bot.yaml`;
- `service-alert-bot.yaml`;
- `cronjob-reporter.yaml`;
- `prometheusrule-alerts.yaml`.

Ключевой safety-механизм:

```yaml
alerting:
  enabled: false
```

То есть существующий deploy не меняется, пока пользователь явно не применит overlay.

## 5. Добавлены Prometheus/Alertmanager конфиги

Созданы:

- `monitoring/alertmanager/alertmanager.yml`;
- `monitoring/prometheus/rules/mega-coder-alerts.yaml`;
- `monitoring/loki/rules/mega-coder-loki-rules.yaml`.

## 6. Добавлены GitLab webhooks

Webhook receiver поддерживает:

- push;
- pipeline success/failed;
- merge request;
- tag push/release.

Project webhook `new user registered` стандартно недоступен, поэтому вместо него документируется ограничение и используются реальные project events.

## 7. Добавлены examples и smoke tests

Созданы:

- `examples/alertmanager-firing.json`;
- `examples/alertmanager-resolved.json`;
- `examples/gitlab-pipeline-failed.json`;
- `examples/gitlab-push.json`;
- `examples/report-example.md`;
- `scripts/smoke_alert_bot.py`.

## 8. Что сделано на живом стенде

На live k3s-стенде выполнено:

- создан Kubernetes Secret `mega-coder-alerting-secret` без сохранения token/chat_id в git;
- собраны и импортированы в k3s локальные images `mega-coder-alert-bot:alerting-demo` и `mega-coder-reporter:alerting-demo`;
- применён Helm overlay `examples/values-alerting-enable.yaml`;
- release `mega` обновлён до revision 15;
- `alert-bot` запущен в namespace `mega-coder`;
- reporter запускается вручную через CronJob и пишет Markdown-отчет;
- test `firing` и `resolved` Alertmanager payload успешно отправлены в Telegram;
- live reporter evidence сохранён в `docs/evidence/reporter-live.md`.

Важная особенность стенда: Telegram API с хоста доступен, но из обычной pod-сети был недоступен. Поэтому для `alert-bot` в demo overlay включён `alerting.alertBot.hostNetwork=true`, а в Deployment strategy используется `Recreate`, чтобы при обновлении не было конфликта порта `8088`.
