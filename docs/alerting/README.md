# Alerting package для защиты

Эта папка собирает всё, что относится к новой части проекта: Telegram notifications, Alertmanager, GitLab webhooks, reporter, evidence и PDF/MD отчёт.

## Что показывать преподавателю

1. `REPORT_ALERTING.md` — полный отчёт по архитектуре и настройке.
2. `SETUP_LOG.md` — что именно было сделано по шагам.
3. `../screenshots/README.md` — список кадров, которые нужно снять после включения реального Telegram chat_id.
4. `../evidence/README.md` — команды для текстового evidence.

## Почему это отдельная папка

Новая alerting-функциональность сделана изолированно:

- в `helm/mega-coder/values.yaml` стоит `alerting.enabled=false`;
- текущий рабочий deploy не меняется, пока overlay `examples/values-alerting-enable.yaml` не применён вручную;
- секреты Telegram/GitLab не лежат в репозитории;
- reporter запускается редко или вручную, чтобы не нагружать кластер.
