# Alerting package для защиты

Эта папка собирает всё, что относится к новой части проекта: Telegram notifications, Alertmanager, GitLab webhooks, reporter, evidence и PDF/MD отчёт.

## Что показывать преподавателю

1. `REPORT_ALERTING.md` — полный отчёт по архитектуре и настройке.
2. `REPORT_ALERTING.pdf` — PDF-версия этого же отчёта со скриншотами для сдачи.
3. `SETUP_LOG.md` — что именно было сделано по шагам.
4. `../screenshots/telegram-status-command.png` — свежий реальный скрин Telegram-команды `/status`.
5. `../screenshots/telegram-help-status-command.png` — свежий реальный скрин Telegram-команд `/help` и `/status`.
6. `../screenshots/README.md` — список кадров и пояснения по скриншотам.
7. `../evidence/README.md` — команды для текстового evidence.

## Почему это отдельная папка

Новая alerting-функциональность сделана изолированно:

- в `helm/mega-coder/values.yaml` стоит `alerting.enabled=false`;
- текущий рабочий deploy не меняется, пока overlay `examples/values-alerting-enable.yaml` не применён вручную;
- секреты Telegram/GitLab не лежат в репозитории;
- reporter запускается редко или вручную, чтобы не нагружать кластер.
