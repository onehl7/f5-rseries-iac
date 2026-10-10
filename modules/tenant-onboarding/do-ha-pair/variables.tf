variable "pair_name" {
  description = "Name identifier of the HA Pair (e.g. Pair-A-LTM, Pair-B-LTM)"
  type        = string
}

variable "local_hostname" {
  description = "Hostname of the local TMOS tenant"
  type        = string
}

variable "peer_hostname" {
  description = "Hostname of the peer TMOS tenant"
  type        = string
}

variable "local_sync_ip" {
  description = "Local Self-IP designated for ConfigSync and unicast failover heartbeats"
  type        = string
}

variable "peer_sync_ip" {
  description = "Peer Self-IP designated for ConfigSync and unicast failover heartbeats"
  type        = string
}

variable "peer_mgmt_ip" {
  description = "Out-of-band management IP address of the peer tenant for initial trust establishment"
  type        = string
}

variable "peer_admin_user" {
  description = "Administrative username on peer tenant"
  type        = string
  default     = "admin"
}

variable "peer_admin_password" {
  description = "Administrative password on peer tenant"
  type        = string
  sensitive   = true
}
