variable "tenant_name" {
  description = "Target AS3 Tenant partition name"
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
