# Architecture Specification: 4x F5 r5900 Multi-Tenant Enterprise Platform

---

## 1. Physical Topology

The platform comprises **4 physical F5 r5900 appliances** deployed as two independent physical pairs across redundant data centers:

```
                  PAIR-A (Data Center 1)                              PAIR-B (Data Center 2)
         [ r5900-A1 ]                [ r5900-A2 ]            [ r5900-B1 ]                [ r5900-B2 ]
     ┌──────────────────┐        ┌──────────────────┐    ┌──────────────────┐        ┌──────────────────┐
     │  Tenant 1: DNS   │<..iq..>│  Tenant 1: DNS   │    │  Tenant 1: DNS   │<..iq..>│  Tenant 1: DNS   │
     │ (Active Anycast) │        │ (Active Anycast) │    │ (Active Anycast) │        │ (Active Anycast) │
     ├──────────────────┤        ├──────────────────┤    ├──────────────────┤        ├──────────────────┤
     │  Tenant 2: LTM   │<======>│  Tenant 2: LTM   │    │  Tenant 2: LTM   │<======>│  Tenant 2: LTM   │
     │     [ACTIVE]     │Sync-FO │    [STANDBY]     │    │     [ACTIVE]     │Sync-FO │    [STANDBY]     │
     └──────────────────┘        └──────────────────┘    └──────────────────┘        └──────────────────┘
              │                                                   │
              └────────────── Cross-Site GSLB iQuery Mesh ────────┘
```

---

## 2. Resource Envelope & Tenant Budget (r5900 Hardware)

Each r5900 appliance provides **16 physical cores (32 hyperthreaded threads)** and **128 GB RAM**:

| Layer / Tenant | vCPUs | RAM | Network & Roles |
| :--- | :--- | :--- | :--- |
| **F5OS-A Host Layer** | 8 | 32 GB | Platform microservices, KVM hypervisor, LACP LAG (`bundle-1`). |
| **Tenant 1: F5 DNS** | 4 | 16 GB | Query-bound DNS resolver & GSLB engine. Anycast BGP on VLAN 500. |
| **Tenant 2: F5 LTM** | 16 | 48 GB | Layer 4–7 traffic, TLS offloading, Intel QAT crypto, AWAF inspection. |
| **Safety Headroom** | 4 | 32 GB | Reserved unallocated buffer for live tenant upgrades and bursts. |

---

## 3. High Availability Mechanics

1. **F5 DNS (Tenant 1)**:
   - All 4 instances (`DNS-A1`, `DNS-A2`, `DNS-B1`, `DNS-B2`) join a unified iQuery mesh sync group (TCP 4353).
   - Ingress queries are load-balanced across all 4 nodes simultaneously using Anycast BGP routes.
2. **F5 LTM (Tenant 2)**:
   - Form independent Active/Standby Sync-Failover pairs:
     - `LTM-A1` (Active) $\leftrightarrow$ `LTM-A2` (Standby) in Pair-A.
     - `LTM-B1` (Active) $\leftrightarrow$ `LTM-B2` (Standby) in Pair-B.
   - If an active appliance fails, the standby peer assumes the Floating Self-IPs and Virtual Server VIPs in sub-second failover.
