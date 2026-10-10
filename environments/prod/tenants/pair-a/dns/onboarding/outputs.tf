output "dns_a1_listener_ip" {
  description = "Configured DNS listener and iQuery self-ip on Node A1"
  value       = module.dns_node_a1.dns_self_ip
}

output "dns_a2_listener_ip" {
  description = "Configured DNS listener and iQuery self-ip on Node A2"
  value       = module.dns_node_a2.dns_self_ip
}
