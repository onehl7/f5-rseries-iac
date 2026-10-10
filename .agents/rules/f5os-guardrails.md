# Guardrails for F5OS-A Platform and Hardware Management
# Scope: Physical rSeries (r5900) Hardware & F5OS-A Operating System

## 1. Hardware Capacity Boundaries
- Never allocate more than 28 vCPUs total across all tenants on an r5900 appliance (leaves 4 vCPUs + 8 host vCPUs as mandatory headroom).
- Memory allocation per r5900 appliance must never exceed 96 GB across all tenants (reserves 32 GB for F5OS-A platform microservices).
- Tenant resource modification (vCPU/RAM resize) requires a tenant reboot. Schedule appropriately during maintenance windows.

## 2. Link Aggregation & VLAN Hygiene
- All production external, internal, and sync interfaces must use LACP LAGs (`lacp-mode active`, minimum interval `1s`).
- Never bind physical ports directly to TMOS tenants; all data plane traffic must be passed as tagged VLANs over LAG bundles.
- Trunk VLANs must be explicitly pruned on F5OS (`allowed-vlans` list). Do not use permissive "all" VLAN forwarding to any tenant.

## 3. High Availability Hardware Separation
- Pair-A (`r5900-A1` and `r5900-A2`) must be physically racked in redundant racks / power distribution zones.
- Pair-B (`r5900-B1` and `r5900-B2`) must reside in an independent secondary data center or availability zone.
- Out-of-band management interfaces must connect to dedicated OOB management switches with dual power supplies.
