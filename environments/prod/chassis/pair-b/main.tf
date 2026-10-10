terraform {
  required_version = ">= 1.6.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "~> 1.18.0"
    }
  }
}

provider "restapi" {
  uri                  = var.f5os_chassis_endpoint
  username             = var.f5os_username
  password             = var.f5os_password
  insecure             = true
  write_returns_object = true
}

# 1. Physical LACP Trunk LAG for Pair-B
module "chassis_lag" {
  source            = "../../../../modules/f5os/lag"
  lag_name          = var.lag_name
  description       = "Production Secondary Data Trunk for Pair-B (Site 2)"
  member_interfaces = var.lag_member_interfaces
  min_links         = 1
}

# 2. Platform VLAN Registrations
module "vlan_external" {
  source    = "../../../../modules/f5os/vlan"
  vlan_id   = 100
  vlan_name = "vlan-external"
}

module "vlan_internal" {
  source    = "../../../../modules/f5os/vlan"
  vlan_id   = 200
  vlan_name = "vlan-internal"
}

module "vlan_dns" {
  source    = "../../../../modules/f5os/vlan"
  vlan_id   = 500
  vlan_name = "vlan-dns-anycast"
}

module "vlan_sync" {
  source    = "../../../../modules/f5os/vlan"
  vlan_id   = 900
  vlan_name = "vlan-ha-sync"
}

# 3. Tenant 1: F5 DNS on r5900-B1 (Active Anycast Node in Site 2)
module "tenant_dns_b1" {
  source             = "../../../../modules/f5os/tenant"
  tenant_name        = "dns-tenant-b1"
  image_name         = var.tmos_image
  cpu_cores          = 4
  memory_mb          = 16384
  mgmt_ip            = "10.2.1.10"
  mgmt_prefix_length = 24
  mgmt_gateway       = "10.2.1.1"
  allowed_vlans      = [500]
  crypto_enabled     = true
}

# 4. Tenant 2: F5 LTM on r5900-B1 (Active Node in Pair-B LTM HA Group)
module "tenant_ltm_b1" {
  source             = "../../../../modules/f5os/tenant"
  tenant_name        = "ltm-tenant-b1"
  image_name         = var.tmos_image
  cpu_cores          = 16
  memory_mb          = 49152
  mgmt_ip            = "10.2.1.20"
  mgmt_prefix_length = 24
  mgmt_gateway       = "10.2.1.1"
  allowed_vlans      = [100, 200, 900]
  crypto_enabled     = true
}
