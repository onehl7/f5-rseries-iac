output "dns_b1_listener_ip" {
  description = "Configured DNS listener and iQuery self-ip on Node B1"
  value       = module.dns_node_b1.dns_self_ip
}

output "dns_b2_listener_ip" {
  description = "Configured DNS listener and iQuery self-ip on Node B2"
  value       = module.dns_node_b2.dns_self_ip
}
