# Screenshot checklist для alerting defense

Файлы ниже нужно снять вручную после включения alerting, потому что реальные Telegram-уведомления и Grafana UI зависят от токена/чата и браузера. На live-стенде уже проверены русские `firing` и `resolved` уведомления с ответом `sent=true`; для отчета лучше снять свежие скриншоты именно этих русских сообщений.

Уже добавлены PNG:

- `docs/screenshots/app-frontend-backend.png` — live UI приложения `http://192.168.1.29:30080`.
- `docs/screenshots/grafana-alert-rules.png` — screenshot evidence с PrometheusRule alert rules.
- `docs/screenshots/alertmanager-config.png` — screenshot evidence с Alertmanager receiver/route YAML.
- `docs/screenshots/gitlab-event-message.png` — screenshot evidence, что GitLab webhook test отправлен в Telegram (`sent=true`).
- `docs/screenshots/report-in-telegram.png` — screenshot evidence reporter/live summary.
- `docs/screenshots/k8s-pods-status.png` — screenshot evidence с live `kubectl get nodes/pods/deploy/svc`.

Осталось снять вручную из Telegram UI, чтобы это были именно настоящие скрины чата:

- `docs/screenshots/telegram-firing-alert.png` — Telegram-сообщение с `Alertmanager: СРАБАТЫВАЕТ`.
- `docs/screenshots/telegram-resolved-alert.png` — Telegram-сообщение с `Alertmanager: ВОССТАНОВЛЕНО`.
