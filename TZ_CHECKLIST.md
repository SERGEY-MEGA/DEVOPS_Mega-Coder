# Чек-лист соответствия ТЗ

Этот файл нужен, чтобы быстро сверить проект с требованиями курса и честно показать, что уже есть в репозитории и что именно поднято на live-стенде.

## 1. Приложение

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| 3+ сервиса | Выполнено | `web`, `api`, `worker`, `redis` |
| Есть HTTP endpoint или UI | Выполнено | `web/html/index.html`, `api/app/main.py`, `worker/app/main.py` |
| Параметризация через env | Выполнено | `api/app/main.py`, `worker/app/main.py`, `web/docker-entrypoint.sh`, `helm/mega-coder/templates/configmap.yaml`, `helm/mega-coder/templates/secret.yaml` |

## 2. GitLab CI/CD

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| `.gitlab-ci.yml` в корне | Выполнено | `.gitlab-ci.yml` |
| Есть stages `pre_build`, `build`, `deploy` | Выполнено | `.gitlab-ci.yml` |
| Используются GitLab Variables | Выполнено | `KUBE_CONFIG`, `APP_SHARED_SECRET`, `CI_REGISTRY*` в `.gitlab-ci.yml` |
| `pre_build` готовит tag/артефакты | Выполнено | job `prepare_image_tag` |
| `build` собирает Docker-образы и пушит в GitLab Registry | Выполнено | jobs `build_api`, `build_web`, `build_worker` |
| `deploy` делает `helm upgrade --install` | Выполнено | job `deploy_helm` |
| Разделение pipeline по веткам/источнику | Выполнено | `workflow: rules` |
| Автоматический rollback | Выполнено | `helm --atomic --cleanup-on-fail` |
| Кэширование слоёв | Выполнено частично | `web` и `worker` используют cache Kaniko, для `api` cache отключён из-за повреждённого cached layer на self-hosted registry |

## 3. Docker

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| Multi-stage build | Выполнено | `api/Dockerfile`, `worker/Dockerfile`, `web/Dockerfile` |
| Минимальный runtime image | Выполнено | `python:3.12.8-slim-bookworm`, `nginx:1.27-alpine` |
| Запуск не от root | Выполнено | `USER 10001:10001`, `nginx` non-root |
| `.dockerignore` | Выполнено | `api/.dockerignore`, `worker/.dockerignore`, `web/.dockerignore` |
| `HEALTHCHECK` | Выполнено | Dockerfile всех сервисов |
| Зафиксированные версии образов | Выполнено | В Dockerfile используются конкретные теги |

## 4. Kubernetes

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| Отдельный namespace | Выполнено | `helm/mega-coder/templates/namespace.yaml` |
| Deployment с минимум 2 репликами приложения | Выполнено | `api`, `web`, `worker` в `values.yaml` и `deployment-*.yaml` |
| Service | Выполнено | `service-api.yaml`, `service-web.yaml`, `service-worker.yaml`, `service-redis.yaml` |
| ConfigMap / Secret | Выполнено | `configmap.yaml`, `secret.yaml` |
| Ingress опционально | Выполнено | `helm/mega-coder/templates/ingress.yaml` |
| Helm chart: `Chart.yaml`, `values.yaml`, templates | Выполнено | `helm/mega-coder/` |
| `helm upgrade --install` идемпотентно | Выполнено | `.gitlab-ci.yml`, `deploy_helm` |

## 5. Топология кластера

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| 1 master + 1 worker | Выполнено в коде, live-демо упрощено | `terraform/main.tf`, `ansible/k3s-cluster.yml`, `ansible/roles/k3s_server/tasks/main.yml`, `ansible/roles/k3s_agent/tasks/main.yml` |

Примечание:
- Для защиты и скриншотов поднят live-стенд на `single-node k3s`.
- Для строгого варианта ТЗ в репозитории подготовлены Terraform и Ansible под `master + worker`.

## 6. Terraform

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| Terraform `>= 1.3` | Выполнено | `terraform/versions.tf` |
| Минимум 2 ВМ | Выполнено в коде | `terraform/main.tf` |
| Переменные | Выполнено | `terraform/variables.tf` |
| Outputs | Выполнено | `terraform/outputs.tf` |
| Локальный state | Выполнено концептуально | Стандартная работа Terraform, state хранится локально |
| VPC + Subnet | Выполнено | `terraform/main.tf` |
| Firewall / Security Group | Выполнено | `terraform/main.tf` |
| SSH key | Выполнено | `terraform/main.tf`, `variables.tf` |

## 7. Ansible

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| Inventory | Выполнено | `ansible/inventory/hosts.ini.example` |
| Структура `roles/` + `site.yml` | Выполнено | `ansible/site.yml`, `ansible/roles/` |
| Идемпотентность | Выполнено | Playbook и роли используют стандартные идемпотентные модули |
| Вариант A: hardening | Выполнено | `ansible/roles/hardening/tasks/main.yml` |
| Обновление пакетов | Выполнено | hardening role |
| `PermitRootLogin no` | Выполнено | hardening role |
| `PasswordAuthentication no` | Выполнено | hardening role |
| UFW | Выполнено | hardening role |
| `auditd` | Выполнено | hardening role |
| `sysctl` hardening | Выполнено | hardening role |

## 8. Monitoring

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| Prometheus | Выполнено | `monitoring/values-kube-prometheus.yaml`, live namespace `monitoring` |
| Grafana | Выполнено | `monitoring/values-kube-prometheus.yaml`, live URL `:30030` |
| Node Exporter | Выполнено | `monitoring/values-kube-prometheus.yaml` |
| Loki | Выполнено | `monitoring/values-loki-stack.yaml` |
| Promtail | Выполнено | `monitoring/values-loki-stack.yaml` |
| kube-state-metrics | Выполнено | `monitoring/values-kube-prometheus.yaml` |
| Системный dashboard | Выполнено | Grafana, `Node Exporter / Nodes` |
| Kubernetes dashboard | Выполнено | Grafana, `Kubernetes / Compute Resources / Namespace (Pods)` |
| Dashboard логов | Выполнено | Grafana, `MEGA CODER / App Logs` |

## 9. Отчёт

| Требование ТЗ | Статус | Где смотреть |
|---------------|--------|--------------|
| Описание приложения и архитектуры | Выполнено | `REPORT.md` |
| Инструкция по запуску | Выполнено | `REPORT.md`, `README.md`, `STRICT_VARIANT.md` |
| Переменные окружения | Выполнено | `REPORT.md` |
| Архитектурная схема | Выполнено | `REPORT.md` |
| Описание pipeline | Выполнено | `REPORT.md`, `.gitlab-ci.yml` |
| Инструкция по Ansible | Выполнено | `REPORT.md` |
| Скриншоты работающего monitoring | Выполнено | `REPORT.md`, `report-assets/` |

## 10. Итог

Короткий честный вывод:

- Репозиторий закрывает основные требования ТЗ по коду, инфраструктуре, CI/CD, Helm, Terraform, Ansible и monitoring.
- Self-hosted GitLab, runner, registry, live k3s-стенд, приложение и Grafana находятся в рабочем состоянии.
- Единственная оговорка для ответа преподавателю: live-демо показано на одном узле `k3s`, а строгая схема `master + worker` подготовлена в коде и документации.
