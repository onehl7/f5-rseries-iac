output "dns_tenant_mgmt_ip" {
  description = "Management IP of DNS Tenant on r5900-A1"
  value       = module.tenant_dns_a1.mgmt_ip
}

output "ltm_tenant_mgmt_ip" {
  description = "Management IP of LTM Tenant on r5900-A1"
  value       = module.tenant_ltm_a1.mgmt_ip
}
