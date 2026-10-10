# Runbook: F5 DNS (GTM) iQuery Mesh Configuration & Validation

---

## 1. Overview
F5 BIG-IP DNS relies on the **iQuery protocol (TCP port 4353)** to establish a secure, bidirectional communication mesh between all DNS listener nodes and LTM traffic-monitoring endpoints across **Pair-A** and **Pair-B**.

---

## 2. iQuery Architecture Mesh

```
       [ DNS-A1 ] <================ iQuery (TCP 4353) ================> [ DNS-B1 ]
           │                                                                 │
         iQuery                                                            iQuery
           │                                                                 │
           ▼                                                                 ▼
       [ LTM-A1 ]                                                        [ LTM-B1 ]
    (reports VIP A)                                                   (reports VIP B)
```

---

## 3. Mutual Certificate Trust Establishment (`bigip_add`)
From `DNS-A1` (`10.1.1.10`), exchange SSL certificates with all participating nodes:

```bash
# Exchange certs with peer DNS nodes
bigip_add 10.1.1.11    # DNS-A2
bigip_add 10.2.1.10    # DNS-B1
bigip_add 10.2.1.11    # DNS-B2

# Exchange certs with LTM clusters to probe VIP health
bigip_add 10.1.1.20    # LTM-A1
bigip_add 10.1.1.21    # LTM-A2
bigip_add 10.2.1.20    # LTM-B1
bigip_add 10.2.1.21    # LTM-B2
```

---

## 4. Verification Commands

```bash
# 1. Verify iQuery connection status
tmsh show gtm iquery

# 2. Verify server object discovery and health
tmsh show gtm server

# 3. Verify WideIP resolution status
tmsh show gtm wideip
```
*Expected Result*: All server objects and data centers display state `Green / Available`.
