# Шпаргалка для защиты проекта MEGA CODER


## 1. Представить проект за 1 минуту

> Я сделал учебный DevOps-проект **MEGA CODER**.  
> Это многосервисное приложение из **трёх сервисов**: `web`, `api`, `worker`, плюс `redis`.  
> Код собирается через **GitLab CI/CD**, образы публикуются в **GitLab Container Registry**, а приложение деплоится в **Kubernetes** через **Helm**.  
> Инфраструктура под кластер описана в **Terraform**, базовая защита серверов автоматизирована через **Ansible**, а мониторинг реализован через **Prometheus + Grafana + Loki + Promtail + Node Exporter + kube-state-metrics**.

## 2. Что по архитектуре

Короткий рассказ:

1. Пользователь открывает `web`.
2. `web` отдаёт статический UI и проксирует `/api/*` в `api`.
3. `api` отдаёт основной backend-ответ, проверяет `worker` и `redis`.
4. `worker` нужен как отдельный вспомогательный микросервис для демонстрации взаимодействия сервисов.
5. Всё это разворачивается в отдельном namespace `mega-coder`.

Если хоите узнать реализацию:

- UI: `web/html/index.html`
- proxy: `web/nginx.conf`
- API: `api/app/main.py`
- worker: `worker/app/main.py`
- K8s-манифесты: `helm/mega-coder/templates/`

## 3. Что по CI/CD

Коротко:

1. В `pre_build` я формирую тег образов.
2. В `build` собираю три Docker-образа и пушу их в GitLab Registry.
3. В `deploy` выполняю `helm upgrade --install`.
4. Деплой идёт только из `main`.
5. Для ускорения включён cache слоёв Kaniko.
6. Для безопасного релиза включён `helm --atomic --cleanup-on-fail`, то есть при неудаче релиз автоматически откатывается.

Что показать:

- `.gitlab-ci.yml`
- `prepare_image_tag`
- `build_api` / `build_web` / `build_worker`
- `deploy_helm`

## 4. Что про Docker

Коротко:

1. Во всех сервисах используется **multi-stage build**.
2. Runtime-слой минимальный: `alpine` или slim.
3. Приложения запускаются **не от root**.
4. Есть `.dockerignore`.
5. Есть `HEALTHCHECK`.

Что показать:

- `api/Dockerfile`
- `worker/Dockerfile`
- `web/Dockerfile`

## 5. Что про Kubernetes и Helm

Коротко:

1. Для приложения выделен отдельный namespace.
2. `api`, `web`, `worker` запускаются минимум в двух репликах.
3. Для сервисов есть `Service`.
4. Конфигурация вынесена в `ConfigMap` и `Secret`.
5. Все параметры вынесены в `values.yaml`.

Что показать:

- `helm/mega-coder/values.yaml`
- `helm/mega-coder/templates/deployment-api.yaml`
- `helm/mega-coder/templates/service-web.yaml`
- `helm/mega-coder/templates/configmap.yaml`
- `helm/mega-coder/templates/secret.yaml`

## 6. Что про Terraform

Коротко:

1. Terraform создаёт **две ВМ**: `master` и `worker`.
2. Также создаются **VPC**, **subnet**, **security group**.
3. Используются `variables.tf` и `outputs.tf`.
4. SSH-ключ пробрасывается в metadata виртуальных машин.

Что показать:

- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`

## 7. Что про Ansible

Коротко:

1. Я выбрал **вариант A — hardening**.
2. Ansible обновляет пакеты.
3. Отключает root-login по SSH.
4. Отключает парольную аутентификацию.
5. Настраивает UFW, auditd и sysctl.
6. Всё сделано идемпотентно через роль.

Что показать:

- `ansible/site.yml`
- `ansible/inventory/hosts.ini.example`
- `ansible/roles/hardening/tasks/main.yml`

## 8. Что про monitoring

Коротко:

1. Для метрик использую `kube-prometheus-stack`.
2. Для логов использую `Loki + Promtail`.
3. Есть обязательные источники данных:
   - Node Exporter
   - kube-state-metrics
   - Prometheus
   - Grafana
   - Loki
4. По ТЗ показываю три типа дашбордов:
   - системный
   - kubernetes
   - логи приложения

Что показать:

- `monitoring/README.md`
- `monitoring/values-kube-prometheus.yaml`
- `monitoring/values-loki-stack.yaml`

## 9. Самые вероятные вопросы

### Почему тут 3+ сервиса?

Потому что по ТЗ нужно минимум три сервиса. У меня это:
- `web`
- `api`
- `worker`

Плюс отдельно используется `redis`.

### Где видно параметризацию через env?

- `api/app/main.py`
- `worker/app/main.py`
- `web/docker-entrypoint.sh`
- `helm/mega-coder/templates/configmap.yaml`
- `helm/mega-coder/templates/secret.yaml`

### Где видно деплой через Helm?

В `.gitlab-ci.yml`, job `deploy_helm`, и в папке `helm/mega-coder/`.

### Где видно использование GitLab Variables?

В `.gitlab-ci.yml` используются:
- `KUBE_CONFIG`
- `APP_SHARED_SECRET`
- встроенные `CI_REGISTRY*`

### Где видно, что Docker не от root?

В Dockerfile:
- `api/Dockerfile`
- `worker/Dockerfile`
- `web/Dockerfile` + запуск процесса от пользователя `nginx`

### Почему вживую показан один сервер, если в ТЗ master + worker?

Короткий ответ:

> Для быстрой живой демонстрации я поднял single-node `k3s` на локальном сервере.
> Но строгий вариант под ТЗ у меня тоже есть в коде: `terraform/main.tf` создаёт две ВМ, а `ansible/k3s-cluster.yml` поднимает `k3s server` на master и `k3s agent` на worker.

Что показать:

- `terraform/main.tf`
- `ansible/k3s-cluster.yml`
- `ansible/roles/k3s_server/tasks/main.yml`
- `ansible/roles/k3s_agent/tasks/main.yml`

### Почему Ansible не поднимает БД?

Потому что выбран **вариант A — hardening**, а не вариант B с БД. Redis в проекте используется как инфраструктурный сервис приложения внутри Kubernetes.

## 10. В каком порядке лучше показывать проект

Самый сильный порядок защиты:

1. `README.md`
2. `PROJECT_MAP.md`
3. `REPORT.md`
4. `.gitlab-ci.yml`
5. `api/app/main.py`
6. `web/nginx.conf` и `web/html/index.html`
7. `helm/mega-coder/values.yaml`
8. `helm/mega-coder/templates/deployment-api.yaml`
9. `terraform/main.tf`
10. `ansible/roles/hardening/tasks/main.yml`
11. `monitoring/README.md`

## 11. Финальная фраза на защите

> В проекте покрыт полный DevOps-цикл: код приложения, контейнеризация, CI/CD, Kubernetes, Helm, Terraform, Ansible и мониторинг.  
> Все обязательные части ТЗ отражены в репозитории и описаны в отчёте.
