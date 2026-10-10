output "ha_pair_status" {
  description = "Pair-A LTM High Availability status"
  value       = module.ha_pair_a.ha_status
}

output "floating_self_ip" {
  description = "Shared floating VIP gateway Self-IP"
  value       = "10.1.100.10"
}
