# MEGA CODER — курсовой стенд DevOps

**Автор:** Сергей · GitLab: [Mega.93/deveps-mega-coder](https://gitlab.com/Mega.93/deveps-mega-coder)

Репозиторий закрывает требования курса: **три сервиса** (API, Web, Worker), **Redis**, **Docker** (multi-stage, non-root, `.dockerignore`), **Helm**, **GitLab CI/CD**, **Terraform** (Yandex Cloud), **Ansible** (харднинг), **мониторинг** (Prometheus, Grafana, Loki, Promtail, Node Exporter, kube-state-metrics).

Полное описание архитектуры, переменных, pipeline и пошаговый запуск — в **[REPORT.md](./REPORT.md)**.

## Быстрые команды

| Задача | Команда |
|--------|---------|
| Сборка API локально | `docker build -t mega-api:local ./api` |
| Рендер Helm без кластера | `helm template mega ./helm/mega-coder -n mega-coder --set global.imageRegistry=... --set images.api.tag=dev --set images.web.tag=dev --set images.worker.tag=dev` |
| Terraform | `cd terraform && terraform init && terraform plan` |
| Ansible | `cd ansible && ansible-galaxy collection install -r requirements.yml && ansible-playbook -i inventory/hosts.ini site.yml` |
| Мониторинг | см. [monitoring/README.md](./monitoring/README.md) |

## GitLab

В **Settings → CI/CD → Variables** задайте:

- `KUBE_CONFIG` — тип **File**, содержимое `kubeconfig`.
- `APP_SHARED_SECRET` — произвольная строка (masked), попадёт в Kubernetes Secret.

Pipeline: **pre_build** → **build** (три образа) → **deploy** (только ветка `main`).
