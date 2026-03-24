# Провайдер: аутентификация через `yc init` или переменные окружения YC_TOKEN / сервисный ключ.
provider "yandex" {
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
}

# --- Сеть: VPC + подсеть (требование ТЗ: сеть/VPC + Subnet) ---
resource "yandex_vpc_network" "this" {
  name        = "mega-coder-net"
  description = "Сеть для master/worker Kubernetes (курсовой стенд)."
}

resource "yandex_vpc_subnet" "this" {
  name           = "mega-coder-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.this.id
  v4_cidr_blocks = [var.subnet_cidr]
}

# --- Security Group: минимально нужные порты (ТЗ + типовой k8s/kubeadm) ---
resource "yandex_vpc_security_group" "this" {
  name        = "mega-coder-sg"
  description = "SSH, API Kubernetes, NodePort, HTTP(S) для проверок."
  network_id  = yandex_vpc_network.this.id

  ingress {
    description    = "SSH"
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = [var.allow_ssh_cidr]
  }

  ingress {
    description    = "Kubernetes API"
    protocol       = "TCP"
    port           = 6443
    v4_cidr_blocks = [var.network_cidr]
  }

  ingress {
    description    = "NodePort диапазон"
    protocol       = "TCP"
    from_port      = 30000
    to_port        = 32767
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description    = "HTTP / HTTPS (Ingress или NodePort 80/443 на ноде)"
    protocol       = "TCP"
    port           = 80
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description    = "HTTPS"
    protocol       = "TCP"
    port           = 443
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description    = "Внутри VPC: TCP (kubelet, CNI и т.д.)."
    protocol       = "TCP"
    from_port      = 0
    to_port        = 65535
    v4_cidr_blocks = [var.network_cidr]
  }

  ingress {
    description    = "Внутри VPC: UDP"
    protocol       = "UDP"
    from_port      = 0
    to_port        = 65535
    v4_cidr_blocks = [var.network_cidr]
  }

  ingress {
    description    = "ICMP внутри VPC"
    protocol       = "ICMP"
    v4_cidr_blocks = [var.network_cidr]
  }

  egress {
    description    = "Исходящий в интернет (образы, пакеты)."
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

locals {
  # SSH-ключ читается с локальной машины и прокидывается в metadata обеих виртуалок.
  ssh_keys = file(pathexpand(var.ssh_public_key_path))
}

data "yandex_compute_image" "ubuntu" {
  family = var.ubuntu_image_family
}

# --- Master node (control plane) ---
resource "yandex_compute_instance" "master" {
  name        = var.master_name
  platform_id = "standard-v3"
  zone        = var.zone

  resources {
    cores         = var.cores
    memory        = var.memory_gb
    core_fraction = 100
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = var.disk_size_gb
      type     = "network-ssd"
    }
  }

  network_interface {
    # NAT включаем, чтобы Ansible и администратор могли подключаться к ноде извне.
    subnet_id          = yandex_vpc_subnet.this.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.this.id]
  }

  metadata = {
    # Сразу создаём доступ по SSH-ключу для пользователя ubuntu.
    ssh-keys = "ubuntu:${local.ssh_keys}"
  }
}

# --- Worker node ---
resource "yandex_compute_instance" "worker" {
  name        = var.worker_name
  platform_id = "standard-v3"
  zone        = var.zone

  resources {
    cores         = var.cores
    memory        = var.memory_gb
    core_fraction = 100
  }

  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.ubuntu.id
      size     = var.disk_size_gb
      type     = "network-ssd"
    }
  }

  network_interface {
    # Worker тоже получает публичный адрес для учебного стенда и простого доступа по SSH.
    subnet_id          = yandex_vpc_subnet.this.id
    nat                = true
    security_group_ids = [yandex_vpc_security_group.this.id]
  }

  metadata = {
    ssh-keys = "ubuntu:${local.ssh_keys}"
  }
}
