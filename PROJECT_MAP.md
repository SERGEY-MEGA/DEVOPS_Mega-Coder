# Карта проекта MEGA CODER

Этот файл нужен для защиты: здесь коротко и по делу описано, **где лежит код**, **что делает каждая папка** и **какие файлы показывать преподавателю**.

## 1. Корень репозитория

| Путь | Что это |
|------|----------|
| `.gitlab-ci.yml` | GitLab CI/CD pipeline: pre_build, build, deploy. |
| `README.md` | Краткий вход в проект, быстрые команды, ссылки на остальные документы. |
| `REPORT.md` | Полный отчёт по курсовому проекту под ТЗ. |
| `PROJECT_MAP.md` | Эта карта репозитория: что где лежит. |
| `DEFENSE_GUIDE.md` | Шпаргалка для устной защиты проекта. |
| `LIVE_DEMO.md` | Как показывать уже поднятый локальный стенд. |
| `STRICT_VARIANT.md` | Как запускать и объяснять строгий вариант `master + worker`. |
| `PITCH_5MIN.md` | Готовый текст короткого выступления. |

## 2. Приложение

### `api/`

Backend на FastAPI.

| Путь | Что делает |
|------|-------------|
| `api/app/main.py` | Основной backend. Эндпоинты `/health`, `/ready`, `/api/info`. Читает env-переменные, проверяет Redis и worker. |
| `api/requirements.txt` | Python-зависимости backend. |
| `api/Dockerfile` | Multi-stage образ backend: builder + runtime, запуск не от root, HEALTHCHECK. |
| `api/.dockerignore` | Уменьшает контекст сборки Docker. |

### `worker/`

Вспомогательный сервис на FastAPI.

| Путь | Что делает |
|------|-------------|
| `worker/app/main.py` | Эндпоинты `/health` и `/work/ping`. Используется backend-ом для демонстрации связи сервисов. |
| `worker/requirements.txt` | Python-зависимости worker. |
| `worker/Dockerfile` | Multi-stage образ worker, non-root, HEALTHCHECK. |
| `worker/.dockerignore` | Уменьшает контекст сборки Docker. |

### `web/`

Frontend + reverse proxy.

| Путь | Что делает |
|------|-------------|
| `web/html/index.html` | Демонстрационный UI. Из браузера вызывает `/api/info`. |
| `web/nginx.conf` | Шаблон конфигурации Nginx: раздача статики и проксирование `/api/` на backend. |
| `web/docker-entrypoint.sh` | Подставляет env-переменные `PORT` и `API_UPSTREAM`, запускает Nginx не от root. |
| `web/Dockerfile` | Multi-stage сборка web-образа, non-root, HEALTHCHECK. |
| `web/.dockerignore` | Уменьшает контекст сборки Docker. |

## 3. Kubernetes и Helm

### `helm/mega-coder/`

Главный Helm chart приложения.

| Путь | Что делает |
|------|-------------|
| `helm/mega-coder/Chart.yaml` | Метаданные чарта. |
| `helm/mega-coder/values.yaml` | Все настраиваемые параметры чарта: теги, реплики, порты, ingress, secret. |
| `helm/mega-coder/templates/_helpers.tpl` | Генерация имён ресурсов и полных путей к Docker-образам. |
| `helm/mega-coder/templates/namespace.yaml` | Namespace приложения. |
| `helm/mega-coder/templates/configmap.yaml` | Несекретные переменные приложения. |
| `helm/mega-coder/templates/secret.yaml` | Kubernetes Secret для `APP_SHARED_SECRET`. |
| `helm/mega-coder/templates/deployment-api.yaml` | Deployment backend с probes и env. |
| `helm/mega-coder/templates/deployment-web.yaml` | Deployment frontend. |
| `helm/mega-coder/templates/deployment-worker.yaml` | Deployment worker. |
| `helm/mega-coder/templates/deployment-redis.yaml` | Deployment Redis. |
| `helm/mega-coder/templates/service-api.yaml` | Service для backend. |
| `helm/mega-coder/templates/service-web.yaml` | Service для frontend. |
| `helm/mega-coder/templates/service-worker.yaml` | Service для worker. |
| `helm/mega-coder/templates/service-redis.yaml` | Service для Redis. |
| `helm/mega-coder/templates/ingress.yaml` | Опциональный Ingress. |

Что показывать на защите:
- `values.yaml`
- любой `deployment-*.yaml`
- `secret.yaml`
- `service-web.yaml`

## 4. CI/CD

### `.gitlab-ci.yml`

Ключевые части pipeline:

| Блок | Что делает |
|------|-------------|
| `stages` | Определяет `pre_build`, `build`, `deploy`. |
| `prepare_image_tag` | Формирует `IMAGE_TAG` и `REGISTRY_BASE`, отдаёт их как dotenv-артефакт. |
| `.kaniko_build` | Общий шаблон job для сборки образов без privileged runner. |
| `build_api`, `build_web`, `build_worker` | Сборка и push трёх образов в GitLab Container Registry. |
| `deploy_helm` | Деплой Helm-чарта в Kubernetes. Использует `helm upgrade --install --atomic`. |

Что показывать на защите:
- `stages`
- `prepare_image_tag`
- любой `build_*`
- `deploy_helm`

## 5. Terraform

### `terraform/`

Поднимает инфраструктуру под Kubernetes в Yandex Cloud.

| Путь | Что делает |
|------|-------------|
| `terraform/versions.tf` | Фиксирует Terraform `>= 1.3` и провайдер Yandex Cloud. |
| `terraform/variables.tf` | Все входные параметры: cloud_id, folder_id, CIDR, SSH key, ресурсы VM. |
| `terraform/main.tf` | Создание VPC, subnet, security group, master VM и worker VM. |
| `terraform/outputs.tf` | Публичные и внутренние IP, плюс готовый сниппет inventory для Ansible. |
| `terraform/terraform.tfvars.example` | Пример файла переменных. |

Что показывать на защите:
- `main.tf` с VPC, subnet, security group
- блок `yandex_compute_instance.master`
- блок `yandex_compute_instance.worker`
- `outputs.tf`

## 6. Ansible

### `ansible/`

Реализует вариант A из ТЗ: hardening серверов.

| Путь | Что делает |
|------|-------------|
| `ansible/site.yml` | Главный playbook. |
| `ansible/ansible.cfg` | Базовая конфигурация Ansible. |
| `ansible/requirements.yml` | Коллекции `ansible.posix` и `community.general`. |
| `ansible/inventory/hosts.ini.example` | Пример inventory для master и worker. |
| `ansible/roles/hardening/tasks/main.yml` | Харднинг: apt upgrade, SSH hardening, UFW, auditd, sysctl. |
| `ansible/roles/hardening/handlers/main.yml` | Перезапуск `sshd` и `auditd` при изменениях. |
| `ansible/k3s-cluster.yml` | Поднимает строгий вариант кластера: `k3s server` на master и `k3s agent` на worker. |
| `ansible/roles/k3s_server/tasks/main.yml` | Автоматизация установки control-plane ноды. |
| `ansible/roles/k3s_agent/tasks/main.yml` | Автоматизация подключения worker к master. |

Что показывать на защите:
- `site.yml`
- `roles/hardening/tasks/main.yml`
- `inventory/hosts.ini.example`

## 7. Monitoring

### `monitoring/`

Файлы для развёртывания мониторинга в Kubernetes.

| Путь | Что делает |
|------|-------------|
| `monitoring/README.md` | Пошаговая инструкция по установке Prometheus, Grafana, Loki, Promtail. |
| `monitoring/values-kube-prometheus.yaml` | Значения для kube-prometheus-stack: Prometheus, Grafana, Node Exporter, kube-state-metrics. |
| `monitoring/values-loki-stack.yaml` | Значения для Loki + Promtail. |

Что показывать на защите:
- `values-kube-prometheus.yaml`
- `values-loki-stack.yaml`
- `monitoring/README.md`

## 8. Папка `deploy/`

`deploy/gitlab-ce/` относится к подготовке вашего GitLab CE сервера и не является обязательной частью курсового приложения. На защите можно упоминать как дополнительную инженерную работу: вы подняли собственный GitLab для CI/CD и хранения репозитория.

## 9. Как быстро ориентироваться на защите

Если преподаватель спрашивает:

- **“Где приложение?”** — показывайте `api/`, `web/`, `worker/`.
- **“Где Kubernetes?”** — показывайте `helm/mega-coder/`.
- **“Где CI/CD?”** — показывайте `.gitlab-ci.yml`.
- **“Где инфраструктура?”** — показывайте `terraform/`.
- **“Где автоматизация?”** — показывайте `ansible/`.
- **“Где мониторинг?”** — показывайте `monitoring/`.
- **“Где полный отчёт?”** — показывайте `REPORT.md`.
