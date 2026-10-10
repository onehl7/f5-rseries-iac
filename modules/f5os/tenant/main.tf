terraform {
  required_version = ">= 1.6.0"
  required_providers {
    restapi = {
      source  = "Mastercard/restapi"
      version = "~> 1.18.0"
    }
  }
}

# F5OS-A Virtual Tenant Lifecycle Resource via RESTCONF
# Controls KVM tenant instance, vCPU/RAM sizing, mgmt network, and VLAN trunk bindings
resource "restapi_object" "f5os_tenant" {
  path = "/restconf/data/f5-tenants:tenants"
  data = jsonencode({
    "tenant" : [
      {
        "name" : var.tenant_name,
        "config" : {
          "name" : var.tenant_name,
          "type" : var.tenant_type,
          "image" : var.image_name,
          "nodes" : [1],
          "mgmt-ip" : var.mgmt_ip,
          "mgmt-prefix-length" : var.mgmt_prefix_length,
          "mgmt-gateway" : var.mgmt_gateway,
          "vlans" : var.allowed_vlans,
          "cpu-cores" : var.cpu_cores,
          "memory" : var.memory_mb,
          "running-state" : var.desired_state,
          "cryptos" : var.crypto_enabled ? "enabled" : "disabled"
        }
      }
    ]
  })
}
