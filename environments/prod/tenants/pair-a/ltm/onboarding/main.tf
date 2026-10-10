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
  alias    = "ltm_a1"
  address  = var.ltm_a1_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

provider "bigip" {
  alias    = "ltm_a2"
  address  = var.ltm_a2_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

# 1. Base System Onboarding on Node A1
module "do_base_a1" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.ltm_a1 }
  hostname  = "ltm-01a.corp.local"
}

# 2. Base System Onboarding on Node A2
module "do_base_a2" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.ltm_a2 }
  hostname  = "ltm-01b.corp.local"
}

# 3. Base Data Plane Networking on Node A1
module "networking_a1" {
  source          = "../../../../../modules/tenant-onboarding/do-networking"
  providers       = { bigip = bigip.ltm_a1 }
  tenant_id       = "ltm-a1"
  default_gateway = "10.1.100.1"
  vlans = [
    { name = "vlan-external", tag = 100, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-internal", tag = 200, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-ha-sync", tag = 900, virtual_interface = "1.1", mtu = 1500 }
  ]
  self_ips = [
    { name = "self-ext-a1", address = "10.1.100.11/24", vlan_name = "vlan-external", is_floating = false, allow_service = "none" },
    { name = "self-ext-float", address = "10.1.100.10/24", vlan_name = "vlan-external", is_floating = true, allow_service = "none" },
    { name = "self-int-a1", address = "10.1.200.11/24", vlan_name = "vlan-internal", is_floating = false, allow_service = "none" },
    { name = "self-sync-a1", address = "10.1.900.11/24", vlan_name = "vlan-ha-sync", is_floating = false, allow_service = "default" }
  ]
  depends_on = [module.do_base_a1]
}

# 4. Base Data Plane Networking on Node A2
module "networking_a2" {
  source          = "../../../../../modules/tenant-onboarding/do-networking"
  providers       = { bigip = bigip.ltm_a2 }
  tenant_id       = "ltm-a2"
  default_gateway = "10.1.100.1"
  vlans = [
    { name = "vlan-external", tag = 100, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-internal", tag = 200, virtual_interface = "1.1", mtu = 1500 },
    { name = "vlan-ha-sync", tag = 900, virtual_interface = "1.1", mtu = 1500 }
  ]
  self_ips = [
    { name = "self-ext-a2", address = "10.1.100.12/24", vlan_name = "vlan-external", is_floating = false, allow_service = "none" },
    { name = "self-int-a2", address = "10.1.200.12/24", vlan_name = "vlan-internal", is_floating = false, allow_service = "none" },
    { name = "self-sync-a2", address = "10.1.900.12/24", vlan_name = "vlan-ha-sync", is_floating = false, allow_service = "default" }
  ]
  depends_on = [module.do_base_a2]
}

# 5. Establish Active/Standby Sync-Failover HA Pairing
module "ha_pair_a" {
  source               = "../../../../../modules/tenant-onboarding/do-ha-pair"
  providers            = { bigip = bigip.ltm_a1 }
  pair_name            = "Pair-A-LTM"
  local_hostname       = "ltm-01a.corp.local"
  peer_hostname        = "ltm-01b.corp.local"
  local_sync_ip        = "10.1.900.11"
  peer_sync_ip         = "10.1.900.12"
  peer_mgmt_ip         = var.ltm_a2_mgmt_ip
  peer_admin_user      = var.tmos_username
  peer_admin_password  = var.tmos_password
  depends_on           = [module.networking_a1, module.networking_a2]
}
