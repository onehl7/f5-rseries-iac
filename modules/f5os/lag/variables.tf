variable "lag_name" {
  description = "Name of the Link Aggregation Group (e.g. lag-trunk-01)"
  type        = string
}

variable "description" {
  description = "Description for the LAG interface"
  type        = string
  default     = "Managed by Terraform F5OS Platform Layer"
}

variable "member_interfaces" {
  description = "List of physical ports belonging to the LAG (e.g. ['1.0', '2.0'])"
  type        = list(string)
}

variable "min_links" {
  description = "Minimum active member links required to keep the LAG up"
  type        = number
  default     = 1
}

variable "lacp_mode" {
  description = "LACP operational mode (ACTIVE or PASSIVE)"
  type        = string
  default     = "ACTIVE"
}
