variable "ltm_a1_mgmt_ip" {
  description = "Management IP for LTM tenant on r5900-A1"
  type        = string
}

variable "ltm_a2_mgmt_ip" {
  description = "Management IP for LTM tenant on r5900-A2"
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
