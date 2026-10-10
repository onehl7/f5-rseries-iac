variable "hostname" {
  description = "Fully qualified domain name for the TMOS tenant"
  type        = string
}

variable "ntp_servers" {
  description = "List of NTP server IP addresses"
  type        = list(string)
  default     = ["10.0.0.1", "10.0.0.2"]
}

variable "timezone" {
  description = "System timezone"
  type        = string
  default     = "UTC"
}

variable "dns_servers" {
  description = "List of DNS recursive resolver IPs"
  type        = list(string)
  default     = ["10.0.0.10", "10.0.0.11"]
}

variable "dns_search_domains" {
  description = "DNS search domain list"
  type        = list(string)
  default     = ["corp.local"]
}

variable "syslog_servers" {
  description = "Remote syslog destinations"
  type = list(object({
    host = string
    port = number
  }))
  default = [
    { host = "10.0.0.50", port = 514 }
  ]
}

variable "snmp_community" {
  description = "SNMP v2c read-only community string"
  type        = string
  default     = "public_mon"
  sensitive   = true
}
