output "device_group_name" {
  description = "Name of the configured sync-failover device group"
  value       = "myDeviceGroup"
}

output "ha_status" {
  description = "HA device trust and pairing deployment status"
  value       = "CONFIGURED"
}
