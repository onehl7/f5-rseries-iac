output "dns_self_ip" {
  description = "Configured DNS self IP address"
  value       = var.dns_self_ip
}

output "status" {
  description = "DNS node onboarding status"
  value       = "CONFIGURED"
}
