output "app_name" {
  description = "Protected application service name"
  value       = var.app_name
}

output "waf_policy_url" {
  description = "Attached WAF policy reference"
  value       = var.waf_policy_url
}
