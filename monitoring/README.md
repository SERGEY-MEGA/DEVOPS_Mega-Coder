# Мониторинг (Prometheus, Grafana, Loki, Promtail, kube-state-metrics, Node Exporter)

Стек ставится **Helm-чартами** в том же Kubernetes-кластере. Ниже — команды и назначение файлов `values-*.yaml`.

Что именно этот стек закрывает по ТЗ:

- `Prometheus` — метрики;
- `Grafana` — дашборды;
- `Node Exporter` — системные метрики нод;
- `kube-state-metrics` — состояние объектов Kubernetes;
- `Loki` — хранение логов;
- `Promtail` — доставка логов контейнеров в Loki.

## Предусловия

- Установлены `helm` 3.x и `kubectl`, настроен `KUBECONFIG`.
- Репозитории чартов:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

## 1) kube-prometheus-stack (Prometheus + Grafana + Node Exporter + kube-state-metrics)

Этот chart выбран потому, что он одним релизом ставит почти весь обязательный monitoring-стек.

```bash
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/values-kube-prometheus.yaml
```

После установки получить пароль админа Grafana:

```bash
kubectl get secret -n monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

Проброс порта Grafana:

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

## 2) Loki + Promtail (логи)

Логи ставятся отдельно, чтобы не смешивать стек метрик и стек логирования.

```bash
helm upgrade --install loki grafana/loki-stack \
  -n monitoring \
  -f monitoring/values-loki-stack.yaml
```

## Дашборды по ТЗ

1. **Системный** — в Grafana импортируйте дашборд **Node Exporter Full** (ID 1860) или используйте встроенные панели из kube-prometheus-stack.
2. **Kubernetes** — дашборд **Kubernetes / Views / Global** (ID 15757) или **Cluster Monitoring for Kubernetes** (7249).
3. **Логи приложения** — в Explore выберите datasource Loki, запрос `{namespace="mega-coder"}`.

Скриншоты этих экранов приложите к отчёту (`REPORT.md`).

## 3) Alerting overlay (опционально)

Alerting добавлен безопасно: базовый стенд не меняется, пока в Helm не включён флаг:

```yaml
alerting:
  enabled: true
```

Связанные файлы:

- `monitoring/prometheus/rules/mega-coder-alerts.yaml` — standalone PrometheusRule manifest.
- `monitoring/alertmanager/alertmanager.yml` — пример Alertmanager route/receiver.
- `monitoring/loki/rules/mega-coder-loki-rules.yaml` — пример Loki ruler rule.
- `examples/values-alerting-enable.yaml` — overlay для ручного включения chart templates.
- `BOT_SETUP.md` — настройка Telegram token/chat_id через Kubernetes Secret.
- `DEMO_ALERTS.md` — как показать firing/resolved и GitLab webhook.

Alertmanager receiver указывает на internal service:

```text
http://mega-mega-coder-alert-bot.mega-coder.svc.cluster.local:8088/webhook/alertmanager
```

Это не открывает новый публичный порт и не ломает текущий Ingress/NodePort.
