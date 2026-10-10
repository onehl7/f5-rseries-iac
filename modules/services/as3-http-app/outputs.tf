output "service_name" {
  description = "Name of the deployed AS3 service"
  value       = var.app_name
}

output "virtual_address" {
  description = "Virtual IP address of the service"
  value       = var.virtual_ip
}
