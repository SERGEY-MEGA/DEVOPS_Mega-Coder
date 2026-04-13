# Demo сценарии для Alerting

## 1. Показать, что alerting безопасно выключен по умолчанию

Открыть `helm/mega-coder/values.yaml` и показать:

```yaml
alerting:
  enabled: false
```

Сказать: “Я не ломаю рабочий деплой; alerting включается отдельным overlay.”

## 2. Включить alerting вручную

```bash
sudo env KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm upgrade --install mega ./helm/mega-coder \
  -n mega-coder \
  -f helm/mega-coder/values.yaml \
  -f examples/values-alerting-enable.yaml
```

## 3. Показать Kubernetes-объекты

```bash
sudo k3s kubectl get deploy,svc,cronjob -n mega-coder
sudo k3s kubectl get prometheusrule -n mega-coder
```

## 4. Вызвать тестовый FIRING alert

```bash
sudo k3s kubectl port-forward -n mega-coder svc/mega-mega-coder-alert-bot 8088:8088
python3 scripts/smoke_alert_bot.py \
  --url http://127.0.0.1:8088/webhook/alertmanager \
  --payload examples/alertmanager-firing.json \
  --secret "$ALERTMANAGER_WEBHOOK_SECRET"
```

Ожидаемый результат: Telegram сообщение с `🔴 Alertmanager: СРАБАТЫВАЕТ` и русским описанием alert.

## 5. Вызвать тестовый RESOLVED alert

```bash
python3 scripts/smoke_alert_bot.py \
  --url http://127.0.0.1:8088/webhook/alertmanager \
  --payload examples/alertmanager-resolved.json \
  --secret "$ALERTMANAGER_WEBHOOK_SECRET"
```

Ожидаемый результат: Telegram сообщение с `🟢 Alertmanager: ВОССТАНОВЛЕНО`.

## 6. Показать GitLab event notification

GitLab UI:

1. Project → Settings → Webhooks.
2. URL: `http://<доступный-url-alert-bot>/webhook/gitlab`.
3. Secret token: значение `GITLAB_WEBHOOK_SECRET`.
4. Events: Push events, Pipeline events, Merge request events, Tag push events.

Локальная проверка через port-forward:

```bash
curl -s -X POST http://127.0.0.1:8088/webhook/gitlab \
  -H "Content-Type: application/json" \
  -H "X-Gitlab-Event: Pipeline Hook" \
  -H "X-Gitlab-Token: $GITLAB_WEBHOOK_SECRET" \
  --data @examples/gitlab-pipeline-failed.json
```

## 7. Показать reporter

```bash
sudo k3s kubectl create job -n mega-coder --from=cronjob/mega-mega-coder-reporter reporter-manual-demo
sudo k3s kubectl logs -n mega-coder job/reporter-manual-demo
```

Если включена отправка отчётов в Telegram (`sendReportToTelegram=true`), краткая версия уйдёт через `/webhook/report`.

Готовый live-пример отчета уже сохранён в `docs/evidence/reporter-live.md`.
