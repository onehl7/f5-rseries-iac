---
name: bigip-tenant-engineer
description: Configures TMOS virtual tenants using Declarative Onboarding (DO) and Application Services 3 (AS3), managing base networking, HA failover pairs, DNS iQuery, and application delivery services.
---

# BIG-IP Tenant Engineer Skill

## Objective
Manage the operational configuration of virtual TMOS tenants hosted on the r5900 appliances:
- **Tenant 1 (F5 DNS)**: Active/Active anycast query engine and global iQuery mesh.
- **Tenant 2 (F5 LTM)**: Active/Standby Sync-Failover HA pairs within Pair-A and Pair-B.

## Key Responsibilities
1. **Declarative Onboarding (DO)**:
   - Self-IPs (Floating and Non-Floating), route domains, static routes.
   - Sync-Failover device trust and network failover heartbeat configuration.
   - System services: NTP, DNS, Syslog, SNMP.
2. **Application Services (AS3)**:
   - Deploy Virtual Servers (HTTP, HTTPS, FastL4).
   - Pools, active health monitors, and pool members.
   - SSL/TLS client/server profiles and certificate binding.
   - AWAF/WAF declarative security policies.
3. **DNS & GSLB Services**:
   - GSLB WideIP declarations, Data Centers, and iQuery server configurations.

## Core IaC Modules
- `modules/tenant-onboarding/do-base`
- `modules/tenant-onboarding/do-networking`
- `modules/tenant-onboarding/do-ha-pair`
- `modules/tenant-onboarding/do-dns-node`
- `modules/services/as3-http-app`
- `modules/services/as3-tcp-app`
- `modules/services/as3-ssl-profile`
- `modules/services/as3-waf-policy`
