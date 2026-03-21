# Все входные параметры инфраструктуры — в variables.tf (требование ТЗ).

variable "cloud_id" {
  description = "Идентификатор облака Yandex Cloud (из консоли или `yc config list`)."
  type        = string
}

variable "folder_id" {
  description = "Идентификатор каталога, в котором создаются ресурсы."
  type        = string
}

variable "zone" {
  description = "Зона доступности для ВМ и сети."
  type        = string
  default     = "ru-central1-a"
}

variable "network_cidr" {
  description = "CIDR VPC для кластера и сервисов."
  type        = string
  default     = "10.10.0.0/16"
}

variable "subnet_cidr" {
  description = "Подсеть в выбранной зоне."
  type        = string
  default     = "10.10.1.0/24"
}

variable "ssh_public_key_path" {
  description = "Путь к публичному ключу SSH на машине, где выполняется terraform apply."
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "master_name" {
  type    = string
  default = "k8s-master"
}

variable "worker_name" {
  type    = string
  default = "k8s-worker"
}

variable "cores" {
  description = "vCPU на каждую ВМ (курс: минимально достаточное значение)."
  type        = number
  default     = 2
}

variable "memory_gb" {
  description = "Гигабайты RAM на ВМ."
  type        = number
  default     = 4
}

variable "disk_size_gb" {
  type    = number
  default = 20
}

variable "ubuntu_image_family" {
  description = "Семейство образа Ubuntu LTS в Yandex Compute."
  type        = string
  default     = "ubuntu-2204-lts"
}

variable "allow_ssh_cidr" {
  description = "Откуда разрешён SSH (0.0.0.0/0 только для отладки; в отчёте рекомендуем свой IP)."
  type        = string
  default     = "0.0.0.0/0"
}
