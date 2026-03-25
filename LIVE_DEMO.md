# Live Demo Checklist

Этот файл нужен для показа уже поднятого стенда на локальном сервере.

Важно:
- В репозитории полная инфраструктура по ТЗ описана через `Terraform + Ansible + Helm + GitLab CI/CD`.
- Для живой демонстрации на домашнем сервере поднят `single-node k3s`.
- Если преподаватель спросит про строгое соответствие топологии `master + worker`, ответ:
  код под 2 ВМ есть в `terraform/`, а локально для быстрой демонстрации используется один узел `k3s`.

## Готовые URL

- Приложение: `http://192.168.1.29:30080`
- Grafana: `http://192.168.1.29:30030`
- Logs dashboard: `http://192.168.1.29:30030/d/mega-coder-logs/mega-coder-app-logs`
- GitLab: `http://192.168.1.29:8080/MEGA/deveps-mega-coder`

## Grafana login

- Логин: `admin`
- Пароль получить командой:

```bash
sudo k3s kubectl get secret monitoring-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

## Команды для показа Kubernetes

Подключение:

```bash
ssh mega@192.168.1.29
sudo -i
```

Общий статус кластера:

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
k3s kubectl get nodes -o wide
k3s kubectl get ns
k3s kubectl get pods -A
helm list -A
```

Приложение:

```bash
k3s kubectl get deploy,svc,cm,secret -n mega-coder
k3s kubectl get pods -n mega-coder -o wide
curl -s http://192.168.1.29:30080/api/info
```

Monitoring:

```bash
k3s kubectl get pods -n monitoring -o wide
k3s kubectl get svc -n monitoring
```

Логи приложения:

```bash
k3s kubectl logs -n mega-coder deploy/mega-mega-coder-api --tail=20
k3s kubectl logs -n mega-coder deploy/mega-mega-coder-web --tail=20
k3s kubectl logs -n mega-coder deploy/mega-mega-coder-worker --tail=20
```

## Что показывать в браузере

1. `http://192.168.1.29:30080`
2. Нажать кнопку `Загрузить данные с API`
3. `http://192.168.1.29:30030`
4. В Grafana открыть:
   - `Node Exporter / Nodes`
   - `Kubernetes / Compute Resources / Namespace (Pods)`
   - `MEGA CODER / App Logs`

## Как объяснять

- `web` это фронтенд на `nginx`, он проксирует `/api/` в backend.
- `api` это основной backend на `FastAPI`.
- `worker` это второй backend-сервис для межсервисного взаимодействия.
- `redis` это вспомогательный сервис состояния.
- Helm-chart поднимает `Deployment + Service + ConfigMap + Secret`.
- Monitoring стек:
  - `Prometheus` собирает метрики
  - `Grafana` показывает дашборды
  - `Node Exporter` даёт системные метрики ноды
  - `kube-state-metrics` даёт метрики объектов Kubernetes
  - `Loki + Promtail` собирают и показывают логи контейнеров
