# Выходные значения для Ansible inventory и отчёта (требование ТЗ: outputs.tf).

output "vpc_id" {
  description = "ID созданной VPC."
  value       = yandex_vpc_network.this.id
}

output "subnet_id" {
  description = "ID подсети."
  value       = yandex_vpc_subnet.this.id
}

output "master_public_ip" {
  description = "Публичный IP master — kubectl с рабочей станции или bastion."
  value       = yandex_compute_instance.master.network_interface[0].nat_ip_address
}

output "master_internal_ip" {
  description = "Внутренний IP master для объявления API и внутреннего трафика."
  value       = yandex_compute_instance.master.network_interface[0].ip_address
}

output "worker_public_ip" {
  description = "Публичный IP worker."
  value       = yandex_compute_instance.worker.network_interface[0].nat_ip_address
}

output "worker_internal_ip" {
  description = "Внутренний IP worker."
  value       = yandex_compute_instance.worker.network_interface[0].ip_address
}

output "ansible_inventory_snippet" {
  description = "Фрагмент для вставки в ansible/inventory/hosts.ini после apply."
  value       = <<-EOT
  [k8s_master]
  ${yandex_compute_instance.master.network_interface[0].nat_ip_address} ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa

  [k8s_workers]
  ${yandex_compute_instance.worker.network_interface[0].nat_ip_address} ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa
  EOT
}
