terraform {
  required_version = ">= 1.6.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "~> 1.18.0"
    }
  }
}

# F5OS-A LACP Link Aggregation Group (LAG) Resource via RESTCONF OpenConfig
resource "restapi_object" "f5os_lag" {
  path = "/restconf/data/openconfig-interfaces:interfaces"
  data = jsonencode({
    "interface" : [
      {
        "name" : var.lag_name,
        "config" : {
          "name" : var.lag_name,
          "type" : "iana-if-type:ieee8023adLag",
          "description" : var.description
        },
        "openconfig-if-aggregate:aggregation" : {
          "config" : {
            "lag-type" : "LACP",
            "min-links" : var.min_links
          }
        }
      }
    ]
  })
}

# Add individual member interfaces to the LAG
resource "restapi_object" "lag_members" {
  for_each = toset(var.member_interfaces)
  path     = "/restconf/data/openconfig-interfaces:interfaces/interface=${each.value}/openconfig-if-ethernet:ethernet"
  data = jsonencode({
    "openconfig-if-aggregate:aggregate-id" : var.lag_name
  })

  depends_on = [restapi_object.f5os_lag]
}
