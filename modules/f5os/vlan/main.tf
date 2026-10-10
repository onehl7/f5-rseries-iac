terraform {
  required_version = ">= 1.6.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "~> 1.18.0"
    }
  }
}

# F5OS Platform VLAN definition via OpenConfig RESTCONF
resource "restapi_object" "f5os_vlan" {
  path = "/restconf/data/openconfig-network-instance:network-instances/network-instance=default/vlans"
  data = jsonencode({
    "vlan" : [
      {
        "vlan-id" : var.vlan_id,
        "config" : {
          "vlan-id" : var.vlan_id,
          "name" : var.vlan_name,
          "status" : "ACTIVE"
        }
      }
    ]
  })
}
