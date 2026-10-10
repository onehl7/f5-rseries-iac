output "lag_name" {
  description = "Name of the configured LAG bundle"
  value       = var.lag_name
}

output "member_interfaces" {
  description = "Physical interfaces participating in the LAG"
  value       = var.member_interfaces
}
