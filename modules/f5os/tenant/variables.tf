variable "tenant_name" {
  description = "Unique name identifier for the virtual tenant (e.g. dns-tenant-a1, ltm-tenant-a1)"
  type        = string
}

variable "tenant_type" {
  description = "Type of virtual tenant (BIG-IP)"
  type        = string
  default     = "BIG-IP"
}

variable "image_name" {
  description = "TMOS qcow2 image registered in F5OS image repository"
  type        = string
  default     = "BIGIP-17.1.1.3-0.0.5.ALL-F5OS.qcow2.zip"
}

variable "cpu_cores" {
  description = "Dedicated vCPU cores assigned to tenant (e.g. 4 for DNS, 16 for LTM)"
  type        = number
}

variable "memory_mb" {
  description = "RAM allocated to the tenant in MB (e.g. 16384, 49152)"
  type        = number
}

variable "mgmt_ip" {
  description = "Static management IPv4 address for the TMOS tenant"
  type        = string
}

variable "mgmt_prefix_length" {
  description = "Subnet prefix length for management network (e.g. 24)"
  type        = number
  default     = 24
}

variable "mgmt_gateway" {
  description = "Default gateway for tenant management network"
  type        = string
}

variable "allowed_vlans" {
  description = "List of VLAN IDs trunked from F5OS into the tenant vNICs"
  type        = list(number)
}

variable "desired_state" {
  description = "Desired operational state of tenant (Deployed, Configured, Provisioned)"
  type        = string
  default     = "Deployed"
}

variable "crypto_enabled" {
  description = "Enable hardware-assisted crypto acceleration passthrough"
  type        = bool
  default     = true
}
