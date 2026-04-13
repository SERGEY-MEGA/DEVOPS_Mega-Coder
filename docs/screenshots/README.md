# Screenshot checklist для alerting defense

Файлы ниже нужно снять вручную после включения alerting, потому что реальные Telegram-уведомления и Grafana UI зависят от токена/чата и браузера. На live-стенде уже проверены русские `firing` и `resolved` уведомления с ответом `sent=true`; для отчета лучше снять свежие скриншоты именно этих русских сообщений.

- `docs/screenshots/grafana-alert-rules.png` — Grafana / Alerting / Alert rules или Prometheus rules screen.
- `docs/screenshots/alertmanager-config.png` — Alertmanager receiver/route или YAML из `monitoring/alertmanager/alertmanager.yml`.
- `docs/screenshots/telegram-firing-alert.png` — Telegram-сообщение с `Alertmanager: СРАБАТЫВАЕТ`.
- `docs/screenshots/telegram-resolved-alert.png` — Telegram-сообщение с `Alertmanager: ВОССТАНОВЛЕНО`.
- `docs/screenshots/gitlab-event-message.png` — Telegram-сообщение по GitLab pipeline/push webhook.
- `docs/screenshots/report-in-telegram.png` — краткий отчёт reporter в Telegram.
- `docs/screenshots/k8s-pods-status.png` — терминал с `kubectl get pods -A`.
