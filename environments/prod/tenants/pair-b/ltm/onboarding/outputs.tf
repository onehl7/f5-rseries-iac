output "ha_pair_status" {
  description = "Pair-B LTM High Availability status"
  value       = module.ha_pair_b.ha_status
}

output "floating_self_ip" {
  description = "Shared floating VIP gateway Self-IP in Pair-B"
  value       = "10.2.100.10"
}
