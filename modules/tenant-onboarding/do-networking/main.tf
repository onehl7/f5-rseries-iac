terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# Declarative Onboarding Networking: VLANs, Self-IPs (Floating/Non-Floating), Routes
resource "bigip_do" "networking_onboarding" {
  do_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-declarative-onboarding/master/schema/latest/base.schema.json",
    "class" : "DO",
    "declaration" : {
      "class" : "Device",
      "schemaVersion" : "1.42.0",
      "async" : true,
      "label" : "TMOS Base Networking for ${var.tenant_id}",
      "Common" : merge(
        {
          "class" : "Tenant",
          "defaultRoute" : {
            "class" : "Route",
            "gw" : var.default_gateway,
            "network" : "default",
            "mtu" : var.default_mtu
          }
        },
        # Dynamic VLAN declarations
        {
          for v in var.vlans : v.name => {
            "class" : "VLAN",
            "tag" : v.tag,
            "interfaces" : [
              {
                "name" : v.virtual_interface,
                "tagged" : true
              }
            ],
            "mtu" : v.mtu
          }
        },
        # Dynamic Self-IP declarations
        {
          for s in var.self_ips : s.name => {
            "class" : "SelfIp",
            "address" : s.address,
            "vlan" : s.vlan_name,
            "trafficGroup" : s.is_floating ? "traffic-group-1" : "traffic-group-local-only",
            "allowService" : s.allow_service
          }
        }
      )
    }
  })

  timeout = 30
}
