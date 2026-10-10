variable "dns_b1_mgmt_ip" {
  description = "Management IP for DNS tenant on r5900-B1"
  type        = string
}

variable "dns_b2_mgmt_ip" {
  description = "Management IP for DNS tenant on r5900-B2"
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
