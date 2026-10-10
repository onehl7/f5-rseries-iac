---
name: f5os-platform-architect
description: Manages F5 rSeries hardware appliance layer (F5OS-A), physical networking, LAGs, VLAN trunks, and virtual tenant container lifecycle.
---

# F5OS Platform Architect Skill

## Objective
Design, provision, and maintain the physical hardware and F5OS-A platform layer for the 4x F5 r5900 appliances across Pair-A (`r5900-A1`, `r5900-A2`) and Pair-B (`r5900-B1`, `r5900-B2`).

## Key Responsibilities
1. **Chassis Interfaces & LAGs**:
   - Configure 100GbE / 25GbE physical interfaces into LACP Link Aggregation Groups (`bundle-1`).
2. **Platform VLANs**:
   - Register VLAN IDs and bind them to the appropriate trunk LAGs with strict trunk pruning.
3. **Tenant Lifecycle**:
   - Deploy and resize Tenant 1 (F5 DNS: 4 vCPUs, 16GB RAM) and Tenant 2 (F5 LTM: 16 vCPUs, 48GB RAM).
   - Assign Management IPs, gateways, DNS servers, and initial credentials.
   - Attach allowed VLANs to each tenant's virtual interface list.

## Core IaC Modules
- `modules/f5os/lag`
- `modules/f5os/vlan`
- `modules/f5os/tenant`

## Execution Context
Always operate within `environments/prod/chassis/pair-a/` or `environments/prod/chassis/pair-b/`. Never modify tenant TMOS base networking directly from this role.
