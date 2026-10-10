output "service_name" {
  description = "Name of the deployed TCP service"
  value       = var.app_name
}

output "virtual_address" {
  description = "Virtual IP address of the TCP service"
  value       = var.virtual_ip
}
