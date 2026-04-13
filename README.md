# MEGA CODER — курсовой стенд DevOps

**Автор:** Сергей  
**Репозиторий:** `http://192.168.1.29:8080/MEGA/deveps-mega-coder`

Репозиторий закрывает требования курса: **три сервиса** (API, Web, Worker), **Redis**, **Docker** (multi-stage, non-root, `.dockerignore`), **Helm**, **GitLab CI/CD**, **Terraform** (Yandex Cloud), **Ansible** (харднинг), **мониторинг** (Prometheus, Grafana, Loki, Promtail, Node Exporter, kube-state-metrics).

Основные документы:

- **[REPORT.md](./REPORT.md)** — полный отчёт по проекту.
- **[REPORT_ALERTING.md](./REPORT_ALERTING.md)** — отдельный отчёт по Prometheus/Alertmanager/Grafana → Telegram alerting.
- **[docs/alerting/REPORT_ALERTING.pdf](./docs/alerting/REPORT_ALERTING.pdf)** — PDF-версия alerting-отчёта для сдачи.
- **[BOT_SETUP.md](./BOT_SETUP.md)** — как безопасно создать Telegram bot secret и не коммитить токены.
- **[DEMO_ALERTS.md](./DEMO_ALERTS.md)** — как показать firing/resolved alert, GitLab event и reporter.
- **[docs/evidence/](./docs/evidence/)** — реальные live evidence: k3s status, Helm release, HTTP smoke, alert-bot logs, reporter output.
- **[RUNBOOKS.md](./RUNBOOKS.md)** — runbook’и по ключевым alert rules.
- **[PROJECT_MAP.md](./PROJECT_MAP.md)** — где лежит код и что делает каждая папка.
- **[DEFENSE_GUIDE.md](./DEFENSE_GUIDE.md)** — шпаргалка для устной защиты.
- **[DEFENSE_2MIN.md](./DEFENSE_2MIN.md)** — сверхкороткий сценарий защиты на 2 минуты.
- **[LIVE_DEMO.md](./LIVE_DEMO.md)** — готовый сценарий показа уже поднятого стенда.
- **[STRICT_VARIANT.md](./STRICT_VARIANT.md)** — строгий путь под ТЗ с `master + worker`.
- **[PITCH_5MIN.md](./PITCH_5MIN.md)** — готовый текст выступления на 3-5 минут.
- **[TZ_CHECKLIST.md](./TZ_CHECKLIST.md)** — сверка проекта с пунктами ТЗ.
- **[DEVOPS_THEORY.md](./DEVOPS_THEORY.md)** — отдельная теория по DevOps, GitLab, YAML, CI/CD, Docker, Kubernetes, Helm, Terraform, Ansible и monitoring.

## Быстрые команды

| Задача | Команда |
|--------|---------|
| Сборка API локально | `docker build -t mega-api:local ./api` |
| Рендер Helm без кластера | `helm template mega ./helm/mega-coder -n mega-coder --set global.imageRegistry=... --set images.api.tag=dev --set images.web.tag=dev --set images.worker.tag=dev` |
| Terraform | `cd terraform && terraform init && terraform plan` |
| Ansible | `cd ansible && ansible-galaxy collection install -r requirements.yml && ansible-playbook -i inventory/hosts.ini site.yml` |
| 2-node k3s | `cd ansible && ansible-playbook -i inventory/hosts.ini k3s-cluster.yml` |
| Мониторинг | см. [monitoring/README.md](./monitoring/README.md) |
| Alerting overlay | `helm upgrade --install mega ./helm/mega-coder -n mega-coder -f helm/mega-coder/values.yaml -f examples/values-alerting-enable.yaml` |

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
- opt-in сборка `alert-bot` и `reporter` через переменную `ENABLE_ALERTING_BUILDS=true`; по умолчанию эти job не запускаются, чтобы не менять рабочий деплой.

## Alerting / Telegram

Alerting-компоненты добавлены как изолированное расширение и **выключены по умолчанию**:

- `services/alert-bot/` — webhook receiver для Alertmanager, Grafana и GitLab webhooks.
- `services/reporter/` — Markdown reporter по Kubernetes/Prometheus/Loki.
- `monitoring/prometheus/rules/mega-coder-alerts.yaml` — alert rules.
- `monitoring/alertmanager/alertmanager.yml` — пример route/receiver до Telegram bridge.
- `examples/values-alerting-enable.yaml` — безопасный overlay для ручного включения.

Секреты `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ALERTMANAGER_WEBHOOK_SECRET`, `GITLAB_WEBHOOK_SECRET` задаются только через Kubernetes Secret или CI/CD Variables. Реальные значения не хранятся в git.

**Отчёт по курсу:** файл **REPORT.md** (при необходимости экспорт в PDF — см. раздел 0 в отчёте).
