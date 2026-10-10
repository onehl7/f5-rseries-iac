variable "tenant_id" {
  description = "Identifier for the tenant instance"
  type        = string
}

variable "default_gateway" {
  description = "Default gateway IPv4 address for data plane routing"
  type        = string
}

variable "default_mtu" {
  description = "MTU for default route"
  type        = number
  default     = 1500
}

variable "vlans" {
  description = "List of VLANs to configure inside the TMOS tenant"
  type = list(object({
    name              = string
    tag               = number
    virtual_interface = string # e.g. "1.1" on tenant
    mtu               = number
  }))
}

variable "self_ips" {
  description = "List of Self-IPs (Floating and Non-Floating) to configure"
  type = list(object({
    name          = string
    address       = string # e.g. "10.1.100.11/24"
    vlan_name     = string
    is_floating   = bool
    allow_service = string # "default", "none", or list
  }))
}
