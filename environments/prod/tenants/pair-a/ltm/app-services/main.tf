terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# The provider connects to the ACTIVE LTM tenant (or the floating admin endpoint)
provider "bigip" {
  address  = var.active_ltm_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

# Migrated eCommerce HTTPS Application Service
module "app_ecommerce_https" {
  source              = "../../../../../modules/services/as3-http-app"
  tenant_name         = "Tenant_LTM_Prod"
  app_name            = "vs_ecommerce_https"
  virtual_ip          = "10.1.100.50"
  virtual_port        = 443
  enable_tls          = true
  lb_method           = "round-robin"
  monitor_send_string = "GET /health HTTP/1.1\\r\\nHost: ecommerce.corp.local\\r\\nConnection: Close\\r\\n\\r\\n"
  monitor_recv_string = "200 OK"
  pool_members = [
    {
      port    = 8080
      servers = ["192.168.10.11", "192.168.10.12"]
    }
  ]
}

# Migrated API Gateway HTTPS Application Service
module "app_api_gateway_https" {
  source              = "../../../../../modules/services/as3-http-app"
  tenant_name         = "Tenant_LTM_Prod"
  app_name            = "vs_api_gateway_https"
  virtual_ip          = "10.1.100.60"
  virtual_port        = 443
  enable_tls          = true
  lb_method           = "least-connections-member"
  monitor_send_string = "GET /health HTTP/1.1\\r\\nHost: api.corp.local\\r\\nConnection: Close\\r\\n\\r\\n"
  monitor_recv_string = "status: ok"
  pool_members = [
    {
      port    = 8443
      servers = ["192.168.20.11", "192.168.20.12"]
    }
  ]
}
