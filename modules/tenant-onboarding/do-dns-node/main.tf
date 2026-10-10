terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# Declarative configuration for Tenant 1 (F5 DNS / GTM Node)
resource "bigip_do" "dns_node_onboarding" {
  do_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-declarative-onboarding/master/schema/latest/base.schema.json",
    "class" : "DO",
    "declaration" : {
      "class" : "Device",
      "schemaVersion" : "1.42.0",
      "async" : true,
      "label" : "F5 DNS Node Onboarding for ${var.dns_hostname}",
      "Common" : {
        "class" : "Tenant",
        "dnsListenerVlan" : {
          "class" : "VLAN",
          "tag" : var.dns_vlan_tag,
          "interfaces" : [
            {
              "name" : var.virtual_interface,
              "tagged" : true
            }
          ]
        },
        "dnsSelfIp" : {
          "class" : "SelfIp",
          "address" : var.dns_self_ip,
          "vlan" : "dnsListenerVlan",
          "trafficGroup" : "traffic-group-local-only",
          "allowService" : ["tcp:4353", "udp:53", "tcp:53"]
        }
      }
    }
  })

  timeout = 30
}
