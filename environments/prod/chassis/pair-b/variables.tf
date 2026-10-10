variable "f5os_chassis_endpoint" {
  description = "F5OS-A RESTCONF API endpoint for Pair-B (https://10.2.0.10)"
  type        = string
}

variable "f5os_username" {
  description = "F5OS-A platform admin username"
  type        = string
  default     = "admin"
}

variable "f5os_password" {
  description = "F5OS-A platform admin password"
  type        = string
  sensitive   = true
}

variable "lag_name" {
  description = "LAG Bundle name"
  type        = string
  default     = "bundle-1"
}

variable "lag_member_interfaces" {
  description = "Physical interfaces participating in LAG"
  type        = list(string)
  default     = ["1.0", "2.0"]
}

variable "tmos_image" {
  description = "TMOS tenant image version"
  type        = string
  default     = "BIGIP-17.1.1.3-0.0.5.ALL-F5OS.qcow2.zip"
}
