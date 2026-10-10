variable "active_ltm_mgmt_ip" {
  description = "Management IP of the Active LTM node in Pair-A (10.1.1.20)"
  type        = string
}

variable "tmos_username" {
  description = "TMOS admin username"
  type        = string
  default     = "admin"
}

variable "tmos_password" {
  description = "TMOS admin password"
  type        = string
  sensitive   = true
}
