# Evidence для alerting

Эта папка содержит реальные текстовые доказательства со стенда и команды, которыми их можно обновить перед защитой.

Уже сохранены:

- `k3s-status-live.txt` — live `nodes`, `pods`, `deploy`, `svc`, `cronjob`, `prometheusrule`;
- `helm-release-live.txt` — live Helm release `mega`, секреты замаскированы;
- `http-smoke-live.txt` — HTTP `200` для app, api, Grafana и GitLab;
- `alert-bot-logs-live.txt` — live логи `alert-bot`;
- `reporter-live.md` — live Markdown-отчет reporter.
- `telegram-tests-live.txt` — итог live-проверок Telegram: firing, resolved, GitLab event, report.

Команды для ручного обновления:

```bash
sudo k3s kubectl get pods -n mega-coder -o wide > docs/evidence/k8s-pods-status.txt
sudo k3s kubectl get prometheusrule -n mega-coder -o yaml > docs/evidence/prometheus-rules.yaml
sudo k3s kubectl get svc,deploy,cronjob -n mega-coder > docs/evidence/alerting-workloads.txt
sudo k3s kubectl logs -n mega-coder deploy/mega-mega-coder-alert-bot --tail=80 > docs/evidence/alert-bot-logs.txt
sudo k3s kubectl create job -n mega-coder --from=cronjob/mega-mega-coder-reporter reporter-manual-demo
sudo k3s kubectl logs -n mega-coder job/reporter-manual-demo > docs/evidence/reporter-output.md
```

Не добавляйте в evidence файлы с настоящими токенами, kubeconfig или chat_id.
