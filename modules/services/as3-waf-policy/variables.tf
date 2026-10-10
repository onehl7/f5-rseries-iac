variable "tenant_name" {
  description = "Target AS3 Tenant partition"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "virtual_ip" {
  description = "Virtual IP address"
  type        = string
}

variable "waf_policy_url" {
  description = "Remote URL or local path to exported JSON/XML AWAF declarative policy"
  type        = string
}

variable "cert_path" {
  description = "Path to certificate on TMOS"
  type        = string
  default     = "/Common/default.crt"
}

variable "pool_members" {
  description = "List of pool members"
  type = list(object({
    port    = number
    servers = list(string)
  }))
}
