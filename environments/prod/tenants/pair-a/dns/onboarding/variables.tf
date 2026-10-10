variable "dns_a1_mgmt_ip" {
  description = "Management IP for DNS tenant on r5900-A1"
  type        = string
}

variable "dns_a2_mgmt_ip" {
  description = "Management IP for DNS tenant on r5900-A2"
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
