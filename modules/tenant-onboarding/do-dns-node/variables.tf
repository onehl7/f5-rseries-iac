variable "dns_hostname" {
  description = "Hostname of the DNS tenant instance (e.g. dns-01a.corp.local)"
  type        = string
}

variable "dns_vlan_tag" {
  description = "VLAN tag for DNS listening & iQuery communication"
  type        = number
}

variable "virtual_interface" {
  description = "Tenant virtual interface for DNS trunk (e.g. 1.1)"
  type        = string
  default     = "1.1"
}

variable "dns_self_ip" {
  description = "Self-IP on DNS tenant with iQuery (4353) and DNS (53) enabled"
  type        = string
}
