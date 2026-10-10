variable "tenant_name" {
  description = "Target AS3 Tenant partition name (e.g. Tenant_LTM_Prod)"
  type        = string
}

variable "app_name" {
  description = "Application name identifier"
  type        = string
}

variable "virtual_ip" {
  description = "Virtual Server VIP IPv4 address"
  type        = string
}

variable "virtual_port" {
  description = "Virtual Server listening port"
  type        = number
  default     = 443
}

variable "enable_tls" {
  description = "Enable TLS offloading (HTTPS service)"
  type        = bool
  default     = true
}

variable "cert_path" {
  description = "Path to certificate in TMOS /Common/ partition or Vault reference"
  type        = string
  default     = "/Common/default.crt"
}

variable "snat_type" {
  description = "Source Network Address Translation type (automap, none)"
  type        = string
  default     = "automap"
}

variable "lb_method" {
  description = "Load balancing algorithm"
  type        = string
  default     = "round-robin"
}

variable "pool_members" {
  description = "List of backend pool member groupings"
  type = list(object({
    port    = number
    servers = list(string)
  }))
}

variable "monitor_interval" {
  description = "Health monitor check frequency in seconds"
  type        = number
  default     = 5
}

variable "monitor_timeout" {
  description = "Health monitor timeout in seconds"
  type        = number
  default     = 16
}

variable "monitor_send_string" {
  description = "HTTP probe string"
  type        = string
  default     = "GET /health HTTP/1.1\\r\\nHost: f5mon.local\\r\\nConnection: Close\\r\\n\\r\\n"
}

variable "monitor_recv_string" {
  description = "HTTP expected response regex"
  type        = string
  default     = "200 OK"
}
