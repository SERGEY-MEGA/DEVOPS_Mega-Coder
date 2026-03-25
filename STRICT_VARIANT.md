# Strict Variant: 2 VM / 1 Master + 1 Worker

Этот файл нужен, если преподаватель требует показать не только live-demo на одном сервере, а именно строгую схему из ТЗ:

- `1 master node`
- `1 worker node`
- инфраструктура через `Terraform`
- автоматизация через `Ansible`
- деплой через `Helm`

## Что уже есть в репозитории

- `terraform/` создаёт:
  - `VPC`
  - `Subnet`
  - `Security Group`
  - `master VM`
  - `worker VM`
- `ansible/site.yml` делает hardening по варианту A
- `ansible/k3s-cluster.yml` поднимает `k3s server + k3s agent`
- `helm/mega-coder/` деплоит приложение
- `monitoring/` разворачивает `Prometheus + Grafana + Loki + Promtail + Node Exporter + kube-state-metrics`

## Почему в live-demo один сервер

На защите можно честно сказать:

> Для быстрой живой демонстрации я поднял single-node `k3s` на локальном сервере.  
> Но строгий production-like путь под ТЗ у меня тоже есть в коде: `Terraform` создаёт две ВМ, `Ansible` делает hardening и поднимает `k3s` на master/worker, после чего приложение и monitoring ставятся через `Helm`.

## Пошаговый запуск строгого варианта

### 1. Поднять две ВМ

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

После `apply` взять:
- `master_public_ip`
- `worker_public_ip`
- `ansible_inventory_snippet`

### 2. Подготовить Ansible inventory

Скопировать `ansible/inventory/hosts.ini.example` в `ansible/inventory/hosts.ini` и вставить IP из `terraform output`.

### 3. Применить hardening

```bash
cd ansible
ansible-galaxy collection install -r requirements.yml
ansible-playbook -i inventory/hosts.ini site.yml
```

### 4. Поднять кластер master + worker

```bash
ansible-playbook -i inventory/hosts.ini k3s-cluster.yml
```

Проверка:

```bash
ssh ubuntu@<master_public_ip>
sudo k3s kubectl get nodes -o wide
```

Ожидаемо: две ноды, одна control-plane и одна worker.

### 5. Поставить приложение

```bash
helm upgrade --install mega ./helm/mega-coder -n mega-coder --create-namespace \
  --set global.imageRegistry=registry.gitlab.example.com/group/project \
  --set images.api.tag=<tag> \
  --set images.web.tag=<tag> \
  --set images.worker.tag=<tag> \
  --set-json 'imagePullSecrets=[{"name":"gitlab-registry"}]' \
  --set secrets.appSharedSecret=<secret>
```

### 6. Поставить monitoring

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring/values-kube-prometheus.yaml

helm upgrade --install loki grafana/loki-stack \
  -n monitoring \
  -f monitoring/values-loki-stack.yaml
```

## Что показывать преподавателю в строгом варианте

### Terraform

- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`

### Ansible

- `ansible/site.yml`
- `ansible/k3s-cluster.yml`
- `ansible/roles/hardening/tasks/main.yml`
- `ansible/roles/k3s_server/tasks/main.yml`
- `ansible/roles/k3s_agent/tasks/main.yml`

### Kubernetes

```bash
sudo k3s kubectl get nodes -o wide
sudo k3s kubectl get pods -A
sudo k3s kubectl get deploy,svc -n mega-coder
helm list -A
```

## Что говорить, если спросят “где именно 2 ноды?”

Короткий ответ:

> Две ноды описаны в `terraform/main.tf`: это `yandex_compute_instance.master` и `yandex_compute_instance.worker`.  
> После создания ВМ они автоматически подготавливаются через `Ansible`: сначала hardening, потом playbook `ansible/k3s-cluster.yml`, который разворачивает `k3s server` на master и `k3s agent` на worker.
