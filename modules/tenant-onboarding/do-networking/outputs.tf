output "configured_vlans" {
  description = "List of configured VLAN names"
  value       = [for v in var.vlans : v.name]
}

output "configured_self_ips" {
  description = "List of configured Self-IP addresses"
  value       = [for s in var.self_ips : s.address]
}
