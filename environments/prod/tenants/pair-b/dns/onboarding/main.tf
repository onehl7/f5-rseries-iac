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
  alias    = "dns_b1"
  address  = var.dns_b1_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

provider "bigip" {
  alias    = "dns_b2"
  address  = var.dns_b2_mgmt_ip
  username = var.tmos_username
  password = var.tmos_password
}

# 1. Base System Onboarding for DNS Node B1
module "do_base_dns_b1" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.dns_b1 }
  hostname  = "dns-02a.corp.local"
}

# 2. Base System Onboarding for DNS Node B2
module "do_base_dns_b2" {
  source    = "../../../../../modules/tenant-onboarding/do-base"
  providers = { bigip = bigip.dns_b2 }
  hostname  = "dns-02b.corp.local"
}

# 3. DNS Listener & iQuery Configuration on Node B1
module "dns_node_b1" {
  source            = "../../../../../modules/tenant-onboarding/do-dns-node"
  providers         = { bigip = bigip.dns_b1 }
  dns_hostname      = "dns-02a.corp.local"
  dns_vlan_tag      = 500
  virtual_interface = "1.1"
  dns_self_ip       = "10.2.50.11/24"
  depends_on        = [module.do_base_dns_b1]
}

# 4. DNS Listener & iQuery Configuration on Node B2
module "dns_node_b2" {
  source            = "../../../../../modules/tenant-onboarding/do-dns-node"
  providers         = { bigip = bigip.dns_b2 }
  dns_hostname      = "dns-02b.corp.local"
  dns_vlan_tag      = 500
  virtual_interface = "1.1"
  dns_self_ip       = "10.2.50.12/24"
  depends_on        = [module.do_base_dns_b2]
}
