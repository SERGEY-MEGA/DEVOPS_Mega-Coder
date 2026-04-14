# Все отчёты и материалы по Telegram / Alertmanager

Один указатель: что открыть на **gitlub.ru** и на **GitHub** (зеркало).

| Площадка | Корень проекта |
|----------|----------------|
| **GitLab (gitlub.ru)** | [MEGA/deveps-mega-coder](https://gitlub.ru/MEGA/deveps-mega-coder) |
| **GitHub** | [SERGEY-MEGA/DEVOPS_Mega-Coder](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/tree/main) |

Ниже — прямые ссылки на файлы в ветке **`main`** (после `git push` откроются в браузере).

---

## Полные отчёты (текст)

| Документ | gitlub.ru | GitHub |
|----------|-----------|--------|
| Развёрнутый отчёт (ТЗ, архитектура, скриншоты `docs/screenshots/`) | [TELEGRAM_ALERTING_FULL_REPORT.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/alert-manager/TELEGRAM_ALERTING_FULL_REPORT.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/alert-manager/TELEGRAM_ALERTING_FULL_REPORT.md) |
| Отчёт прямо в `alert-manager/` | [REPORT_ALERTING.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/alert-manager/REPORT_ALERTING.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/alert-manager/REPORT_ALERTING.md) |
| PDF прямо в `alert-manager/` | [REPORT_ALERTING.pdf](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/alert-manager/REPORT_ALERTING.pdf) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/alert-manager/REPORT_ALERTING.pdf) |
| Дубликат в `docs/alerting/` | [REPORT_ALERTING.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/alerting/REPORT_ALERTING.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/alerting/REPORT_ALERTING.md) |
| PDF в `docs/alerting/` | [REPORT_ALERTING.pdf](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/alerting/REPORT_ALERTING.pdf) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/alerting/REPORT_ALERTING.pdf) |
| Журнал внедрения alerting | [SETUP_LOG.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/alerting/SETUP_LOG.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/alerting/SETUP_LOG.md) |

---

## Живые скриншоты чата + пошаговая настройка

| Документ | gitlub.ru | GitHub |
|----------|-----------|--------|
| **Корневая папка `alert-manager/`** (скрины Telegram, описание подключения) | [README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/alert-manager/README.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/alert-manager/README.md) |
| Свежий скрин `/status` | [telegram-04-status-command.png](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/alert-manager/telegram-04-status-command.png) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/alert-manager/telegram-04-status-command.png) |
| Свежий скрин `/help` + `/status` | [telegram-05-help-status-command.png](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/alert-manager/telegram-05-help-status-command.png) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/alert-manager/telegram-05-help-status-command.png) |
| Указатель в `docs/alert-manager/` | [README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/alert-manager/README.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/alert-manager/README.md) |

PNG в **`alert-manager/`**: `telegram-01-*.png` … `telegram-05-*.png` — открывайте через **Raw** или **View** в том же репозитории.

---

## Минимальный бот (локальный тест без k8s)

| Документ | gitlub.ru | GitHub |
|----------|-----------|--------|
| `minimal-alert-bot` — команды, curl, Docker | [README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/minimal-alert-bot/README.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/minimal-alert-bot/README.md) |

---

## Настройка секретов и демо

| Документ | gitlub.ru | GitHub |
|----------|-----------|--------|
| Создание бота и Secret (без токена в git) | [BOT_SETUP.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/BOT_SETUP.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/BOT_SETUP.md) |
| Сценарии firing / resolved / GitLab / reporter | [DEMO_ALERTS.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/DEMO_ALERTS.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/DEMO_ALERTS.md) |
| Чеклист скриншотов | [docs/screenshots/README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/screenshots/README.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/screenshots/README.md) |
| Обзор папки `docs/alerting/` | [README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/alerting/README.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/alerting/README.md) |

---

## Evidence (логи и проверки)

| Документ | gitlub.ru | GitHub |
|----------|-----------|--------|
| Описание папки evidence | [docs/evidence/README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/evidence/README.md) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/evidence/README.md) |
| Итог проверок Telegram | [telegram-tests-live.txt](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/evidence/telegram-tests-live.txt) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/evidence/telegram-tests-live.txt) |
| Логи alert-bot | [alert-bot-logs-live.txt](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/docs/evidence/alert-bot-logs-live.txt) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/docs/evidence/alert-bot-logs-live.txt) |

---

## Код сервисов

| Путь | gitlub.ru | GitHub |
|------|-----------|--------|
| Production `alert-bot` | [services/alert-bot/](https://gitlub.ru/MEGA/deveps-mega-coder/-/tree/main/services/alert-bot) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/tree/main/services/alert-bot) |
| Reporter | [services/reporter/](https://gitlub.ru/MEGA/deveps-mega-coder/-/tree/main/services/reporter) | [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/tree/main/services/reporter) |

---

**Корень проекта:** [README.md](https://gitlub.ru/MEGA/deveps-mega-coder/-/blob/main/README.md) · [GitHub](https://github.com/SERGEY-MEGA/DEVOPS_Mega-Coder/blob/main/README.md)
