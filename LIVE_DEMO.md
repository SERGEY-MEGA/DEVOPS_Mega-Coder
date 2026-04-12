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
- DevOps dashboard: `http://192.168.1.29:30030/d/mega-coder-devops/mega-coder-devops-overview`
- Logs dashboard: `http://192.168.1.29:30030/d/mega-coder-logs/mega-coder-app-logs`
- GitLab: `http://192.168.1.29:8080/MEGA/deveps-mega-coder`

## Grafana login

- Логин: `admin`
- Пароль: `MegaGrafana2026`

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
   - `MEGA CODER / DevOps Overview`
   - `MEGA CODER / App Logs`, если нужно отдельно показать Loki-логи

Стандартные dashboards Grafana открывать не обязательно: в single-node k3s часть чужих панелей может быть пустой. Для ТЗ достаточно подготовленного dashboard `MEGA CODER / DevOps Overview`, потому что он показывает system metrics, Kubernetes replicas и Loki logs.

## Лучший порядок показа на защите

1. Открыть проект в GitLab и показать [README.md](/Users/sergejmegeran/Desktop/devops%20peresdacha/README.md), чтобы быстро объяснить состав проекта.
2. Открыть [PROJECT_MAP.md](/Users/sergejmegeran/Desktop/devops%20peresdacha/PROJECT_MAP.md) и коротко показать, где лежат `api`, `web`, `worker`, `helm`, `terraform`, `ansible`, `monitoring`.
3. Открыть [.gitlab-ci.yml](/Users/sergejmegeran/Desktop/devops%20peresdacha/.gitlab-ci.yml) и сказать: `pre_build -> build -> deploy`.
4. Открыть [api/app/main.py](/Users/sergejmegeran/Desktop/devops%20peresdacha/api/app/main.py), [worker/app/main.py](/Users/sergejmegeran/Desktop/devops%20peresdacha/worker/app/main.py), [web/nginx.conf](/Users/sergejmegeran/Desktop/devops%20peresdacha/web/nginx.conf) и за 30-40 секунд объяснить роли сервисов.
5. Переключиться в терминал и показать `k3s kubectl get nodes -o wide`, потом `k3s kubectl get pods -A`, потом `helm list -A`.
6. Показать namespace приложения: `k3s kubectl get deploy,svc,cm,secret -n mega-coder`.
7. Открыть приложение: `http://192.168.1.29:30080`.
8. Нажать `Загрузить данные с API`, затем при желании открыть `http://192.168.1.29:30080/api/info`.
9. Открыть Grafana: `http://192.168.1.29:30030`.
10. В Grafana открыть `MEGA CODER / DevOps Overview`: там уже собраны CPU/RAM/Disk/Network, pod count, deployment replicas и Loki logs.
11. Если преподаватель хочет отдельный логовый экран, открыть `MEGA CODER / App Logs`.
12. Если спросят про строгий вариант ТЗ, открыть [STRICT_VARIANT.md](/Users/sergejmegeran/Desktop/devops%20peresdacha/STRICT_VARIANT.md) и показать `terraform/` + `ansible/k3s-cluster.yml`.

## Как быстро поднять стенд заново и показать

Если сервер уже включен и Docker/k3s живы, обычно достаточно проверить:

```bash
ssh mega@192.168.1.29
sudo -i
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
k3s kubectl get pods -A
```

Если все pod'ы `Running`, стенд уже готов.

Если нужно просто перезапустить приложение:

```bash
ssh mega@192.168.1.29
sudo -i
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
k3s kubectl rollout restart deployment/mega-mega-coder-api -n mega-coder
k3s kubectl rollout restart deployment/mega-mega-coder-web -n mega-coder
k3s kubectl rollout restart deployment/mega-mega-coder-worker -n mega-coder
k3s kubectl rollout status deployment/mega-mega-coder-api -n mega-coder --timeout=180s
k3s kubectl rollout status deployment/mega-mega-coder-web -n mega-coder --timeout=180s
k3s kubectl rollout status deployment/mega-mega-coder-worker -n mega-coder --timeout=180s
```

После этого открыть:

- `http://192.168.1.29:30080`
- `http://192.168.1.29:30030`

Если нужно быстро доказать, что приложение отвечает:

```bash
curl -I http://192.168.1.29:30080
curl -s http://192.168.1.29:30080/api/info
```

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
