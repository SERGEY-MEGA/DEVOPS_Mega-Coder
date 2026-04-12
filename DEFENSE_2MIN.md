# Сценарий защиты на 2 минуты

Этот файл нужен для самого короткого и уверенного показа без лишних переключений.

## 1. Что открыть по порядку

1. `README.md`
2. `PROJECT_MAP.md`
3. `.gitlab-ci.yml`
4. `http://192.168.1.29:8080/MEGA/deveps-mega-coder/-/pipelines`
5. Терминал с SSH на сервер
6. `http://192.168.1.29:30080`
7. `http://192.168.1.29:30030`

## 2. Что сказать

> Я сделал DevOps-проект `MEGA CODER`.  
> Это многосервисное приложение из `web`, `api`, `worker` и `redis`.  
> Код собирается через GitLab CI/CD, Docker-образы пушатся в GitLab Container Registry, а деплой идёт в Kubernetes через Helm.  
> Инфраструктура под строгий вариант ТЗ описана в Terraform, hardening автоматизирован через Ansible, мониторинг собран на Prometheus, Grafana, Loki, Promtail, Node Exporter и kube-state-metrics.

## 3. Какие 4 команды показать

```bash
ssh mega@192.168.1.29
sudo -i
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
k3s kubectl get nodes -o wide
```

Потом:

```bash
k3s kubectl get pods -A
helm list -A
k3s kubectl get deploy,svc,cm,secret -n mega-coder
```

## 4. Что сделать в браузере

1. На странице pipeline показать свежий зелёный `success`.
2. Открыть приложение `http://192.168.1.29:30080`.
3. Нажать кнопку `Загрузить данные с API`.
4. Открыть Grafana `http://192.168.1.29:30030`.
5. Логин: `admin`
6. Пароль: `MegaGrafana2026`
7. Показать:
   - `MEGA CODER / DevOps Overview`
   - `MEGA CODER / App Logs`, если попросят отдельно показать Loki

Если в стандартных dashboards Grafana есть пустые панели, их не открывать: для сдачи подготовлен отдельный dashboard `MEGA CODER / DevOps Overview`, где собраны нужные по ТЗ CPU/RAM/Disk/Network, Kubernetes replicas и Loki logs.

## 5. Финальная фраза

> В проекте показан полный DevOps-цикл: приложение, Docker, GitLab CI/CD, Registry, Kubernetes, Helm, Terraform, Ansible и monitoring.  
> Live-стенд рабочий, а строгий вариант под 2 узла также подготовлен в репозитории.
