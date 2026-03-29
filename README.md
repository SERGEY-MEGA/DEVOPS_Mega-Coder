# MEGA CODER — курсовой стенд DevOps

**Автор:** Сергей  
**Репозиторий:** `http://192.168.1.29:8080/MEGA/deveps-mega-coder`

Репозиторий закрывает требования курса: **три сервиса** (API, Web, Worker), **Redis**, **Docker** (multi-stage, non-root, `.dockerignore`), **Helm**, **GitLab CI/CD**, **Terraform** (Yandex Cloud), **Ansible** (харднинг), **мониторинг** (Prometheus, Grafana, Loki, Promtail, Node Exporter, kube-state-metrics).

Основные документы:

- **[REPORT.md](./REPORT.md)** — полный отчёт по проекту.
- **[PROJECT_MAP.md](./PROJECT_MAP.md)** — где лежит код и что делает каждая папка.
- **[DEFENSE_GUIDE.md](./DEFENSE_GUIDE.md)** — шпаргалка для устной защиты.
- **[LIVE_DEMO.md](./LIVE_DEMO.md)** — готовый сценарий показа уже поднятого стенда.
- **[STRICT_VARIANT.md](./STRICT_VARIANT.md)** — строгий путь под ТЗ с `master + worker`.
- **[PITCH_5MIN.md](./PITCH_5MIN.md)** — готовый текст выступления на 3-5 минут.

## Быстрые команды

| Задача | Команда |
|--------|---------|
| Сборка API локально | `docker build -t mega-api:local ./api` |
| Рендер Helm без кластера | `helm template mega ./helm/mega-coder -n mega-coder --set global.imageRegistry=... --set images.api.tag=dev --set images.web.tag=dev --set images.worker.tag=dev` |
| Terraform | `cd terraform && terraform init && terraform plan` |
| Ansible | `cd ansible && ansible-galaxy collection install -r requirements.yml && ansible-playbook -i inventory/hosts.ini site.yml` |
| 2-node k3s | `cd ansible && ansible-playbook -i inventory/hosts.ini k3s-cluster.yml` |
| Мониторинг | см. [monitoring/README.md](./monitoring/README.md) |

## Важная оговорка для защиты

- Для **живой демонстрации** в локальной сети поднят `single-node k3s` стенд.
- Для **строгого варианта ТЗ** в репозитории есть код под `2 VM / 1 master + 1 worker`: `terraform/` + `ansible/k3s-cluster.yml`.

## GitLab CI/CD

В **Settings → CI/CD → Variables** задайте:

- `KUBE_CONFIG` — тип **File**, содержимое `kubeconfig`.
- `APP_SHARED_SECRET` — произвольная строка (masked), попадёт в Kubernetes Secret.

На локальном self-hosted GitLab стенде уже настроены:

- project runner `server-docker-runner` (Docker executor);
- GitLab Container Registry `192.168.1.29:5050`;
- обязательные variables `KUBE_CONFIG` и `APP_SHARED_SECRET`.

Pipeline: **pre_build** → **build** (три образа) → **deploy** (только ветка `main`).  
Дополнительно включены:

- cache слоёв сборки через Kaniko;
- разделение `merge_request` / branch pipeline через `workflow: rules`;
- автоматический rollback релиза через `helm --atomic --cleanup-on-fail`.

**Отчёт по курсу:** файл **REPORT.md** (при необходимости экспорт в PDF — см. раздел 0 в отчёте).
