output "tenant_name" {
  description = "Name of the provisioned tenant"
  value       = var.tenant_name
}

output "mgmt_ip" {
  description = "Management IP address of the provisioned tenant"
  value       = var.mgmt_ip
}

output "cpu_cores" {
  description = "Assigned vCPUs"
  value       = var.cpu_cores
}

output "memory_mb" {
  description = "Assigned RAM in MB"
  value       = var.memory_mb
}
