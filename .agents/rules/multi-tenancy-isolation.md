# Multi-Tenancy Isolation and Failure Domain Governance
# Scope: r5900 Virtual Tenants (DNS & LTM) across Pair-A & Pair-B

## 1. Failure Domain Isolation
- Each virtual tenant is an independent TMOS instance with its own management IP, kernel memory, and routing table.
- A failure or crash of Tenant 1 (DNS) must never impact the packet processing or health of Tenant 2 (LTM).
- High Availability is strictly tenant-scoped:
  - `LTM-A1` pairs exclusively with `LTM-A2` (Sync-Failover Group).
  - `LTM-B1` pairs exclusively with `LTM-B2` (Sync-Failover Group).
  - Cross-pair failover for LTM is NOT allowed; cross-site resilience is managed at the DNS layer via GSLB WideIPs.

## 2. DNS Mesh Governance
- Tenant 1 (F5 DNS) instances across all 4 appliances (`DNS-A1`, `DNS-A2`, `DNS-B1`, `DNS-B2`) form a unified iQuery mesh sync group.
- Port TCP 4353 (iQuery) must be permitted between all 4 DNS tenant self-IPs and between DNS tenants and LTM self-IPs.
- Listener IPs must be advertised via BGP Anycast to ensure instant failure diversion.
