# Мониторинг (Prometheus, Grafana, Loki, Promtail, kube-state-metrics, Node Exporter)

Стек ставится **Helm-чартами** в том же Kubernetes-кластере. Ниже — команды и назначение файлов `values-*.yaml`.

## Предусловия

- Установлены `helm` 3.x и `kubectl`, настроен `KUBECONFIG`.
- Репозитории чартов:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

## 1) kube-prometheus-stack (Prometheus + Grafana + Node Exporter + kube-state-metrics)

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
