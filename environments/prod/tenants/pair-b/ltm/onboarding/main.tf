terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

provider "bigip" {
  alias    = "ltm_b1"
  address  = var.ltm_b1_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

provider "bigip" {
  alias    = "ltm_b2"
  address  = var.ltm_b2_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

# 1. Base System Onboarding on Node B1
module "do_base_b1" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.ltm_b1 }
  hostname  = "ltm-02a.corp.local"
}

# 2. Base System Onboarding on Node B2
module "do_base_b2" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.ltm_b2 }
  hostname  = "ltm-02b.corp.local"
}

# 3. Base Data Plane Networking on Node B1
module "networking_b1" {
  source          = "../../../../../modules/tenant-onboarding/do-networking"
  providers       = { bigip = bigip.ltm_b1 }
  tenant_id       = "ltm-b1"
  default_gateway = "10.2.100.1"
  vlans = [
    { name = "vlan-external", tag = 100, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-internal", tag = 200, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-ha-sync", tag = 900, virtual_interface = "1.1", mtu = 1500 }
  ]
  self_ips = [
    { name = "self-ext-b1", address = "10.2.100.11/24", vlan_name = "vlan-external", is_floating = false, allow_service = "none" },
    { name = "self-ext-float", address = "10.2.100.10/24", vlan_name = "vlan-external", is_floating = true, allow_service = "none" },
    { name = "self-int-b1", address = "10.2.200.11/24", vlan_name = "vlan-internal", is_floating = false, allow_service = "none" },
    { name = "self-sync-b1", address = "10.2.900.11/24", vlan_name = "vlan-ha-sync", is_floating = false, allow_service = "default" }
  ]
  depends_on = [module.do_base_b1]
}

# 4. Base Data Plane Networking on Node B2
module "networking_b2" {
  source          = "../../../../../modules/tenant-onboarding/do-networking"
  providers       = { bigip = bigip.ltm_b2 }
  tenant_id       = "ltm-b2"
  default_gateway = "10.2.100.1"
  vlans = [
    { name = "vlan-external", tag = 100, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-internal", tag = 200, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-ha-sync", tag = 900, virtual_interface = "1.1", mtu = 1500 }
  ]
  self_ips = [
    { name = "self-ext-b2", address = "10.2.100.12/24", vlan_name = "vlan-external", is_floating = false, allow_service = "none" },
    { name = "self-int-b2", address = "10.2.200.12/24", vlan_name = "vlan-internal", is_floating = false, allow_service = "none" },
    { name = "self-sync-b2", address = "10.2.900.12/24", vlan_name = "vlan-ha-sync", is_floating = false, allow_service = "default" }
  ]
  depends_on = [module.do_base_b2]
}

# 5. Establish Active/Standby Sync-Failover HA Pairing
module "ha_pair_b" {
  source               = "../../../../../modules/tenant-onboarding/do-ha-pair"
  providers            = { bigip = bigip.ltm_b1 }
  pair_name            = "Pair-B-LTM"
  local_hostname       = "ltm-02a.corp.local"
  peer_hostname        = "ltm-02b.corp.local"
  local_sync_ip        = "10.2.900.11"
  peer_sync_ip         = "10.2.900.12"
  peer_mgmt_ip         = var.ltm_b2_mgmt_ip
  peer_admin_user      = var.tmos_username
  peer_admin_password  = var.tmos_password
  depends_on           = [module.networking_b1, module.networking_b2]
}
