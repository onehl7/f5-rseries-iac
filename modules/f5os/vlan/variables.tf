variable "vlan_id" {
  description = "IEEE 802.1Q VLAN Tag (1 - 4094)"
  type        = number
  validation {
    condition     = var.vlan_id >= 1 && var.vlan_id <= 4094
    error_message = "VLAN ID must be between 1 and 4094."
  }
}

variable "vlan_name" {
  description = "Descriptive name for the platform VLAN"
  type        = string
}
