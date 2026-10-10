terraform {
  required_version = ">= 1.6.0"
  required_providers {
    bigip = {
      source  = "f5networks/bigip"
      version = "~> 1.22.0"
    }
  }
}

# Declarative AS3 FastL4 / TCP Application Service
resource "bigip_as3" "tcp_service" {
  as3_json = jsonencode({
    "$schema" : "https://raw.githubusercontent.com/F5Networks/f5-appsvcs-extension/master/schema/latest/as3-schema.json",
    "class" : "AS3",
    "action" : "deploy",
    "persist" : true,
    "declaration" : {
      "class" : "ADC",
      "schemaVersion" : "3.50.0",
      "id" : "urn:f5:rseries:${var.tenant_name}:${var.app_name}",
      (var.tenant_name) : {
        "class" : "Tenant",
        (var.app_name) : {
          "class" : "Application",
          "template" : "generic",
          "serviceMain" : {
            "class" : "Service_TCP",
            "virtualAddresses" : [var.virtual_ip],
            "virtualPort" : var.virtual_port,
            "pool" : "tcp_pool"
          },
          "tcp_pool" : {
            "class" : "Pool",
            "loadBalancingMode" : var.lb_method,
            "monitors" : ["tcp"],
            "members" : [
              for m in var.pool_members : {
                "servicePort" : m.port,
                "serverAddresses" : m.servers
              }
            ]
          }
        }
      }
    }
  })
}
