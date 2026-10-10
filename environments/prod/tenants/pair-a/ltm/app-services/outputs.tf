output "ecommerce_service_vip" {
  description = "Virtual IP for eCommerce HTTPS"
  value       = module.app_ecommerce_https.virtual_address
}

output "api_gateway_service_vip" {
  description = "Virtual IP for API Gateway HTTPS"
  value       = module.app_api_gateway_https.virtual_address
}
