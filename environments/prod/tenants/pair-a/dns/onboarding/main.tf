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
  alias    = "dns_a1"
  address  = var.dns_a1_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

provider "bigip" {
  alias    = "dns_a2"
  address  = var.dns_a2_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

# 1. Base System Onboarding for DNS Node A1
module "do_base_dns_a1" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.dns_a1 }
  hostname  = "dns-01a.corp.local"
}

# 2. Base System Onboarding for DNS Node A2
module "do_base_dns_a2" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.dns_a2 }
  hostname  = "dns-01b.corp.local"
}

# 3. DNS Listener & iQuery Configuration on Node A1
module "dns_node_a1" {
  source            = "../../../../../modules/tenant-onboarding/do-dns-node"
  providers         = { bigip = bigip.dns_a1 }
  dns_hostname      = "dns-01a.corp.local"
  dns_vlan_tag      = 500
  virtual_interface = "1.1"
  dns_self_ip       = "10.1.50.11/24"
  depends_on        = [module.do_base_dns_a1]
}

# 4. DNS Listener & iQuery Configuration on Node A2
module "dns_node_a2" {
  source            = "../../../../../modules/tenant-onboarding/do-dns-node"
  providers         = { bigip = bigip.dns_a2 }
  dns_hostname      = "dns-01b.corp.local"
  dns_vlan_tag      = 500
  virtual_interface = "1.1"
  dns_self_ip       = "10.1.50.12/24"
  depends_on        = [module.do_base_dns_a2]
}
