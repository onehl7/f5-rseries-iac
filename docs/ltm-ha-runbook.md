# Runbook: LTM Active/Standby HA Failover Testing and Verification

---

## 1. Overview
This runbook guides network engineers through verifying high availability failover between `LTM-A1` (Active) and `LTM-A2` (Standby) on Pair-A (and symmetrically on Pair-B).

---

## 2. Pre-Failover Health Checks
Run the following commands on `LTM-A1` (`10.1.1.20`):

```bash
# 1. Check failover status
tmsh show cm failover-status

# 2. Check sync status
tmsh show cm sync-status

# 3. Check traffic group status
tmsh show cm traffic-group traffic-group-1
```
*Expected Result*: Node A1 shows `Active`, Node A2 shows `Standby`, and Device Group is `In Sync`.

---

## 3. Graceful Failover Drill
To initiate a controlled failover from `LTM-A1` to `LTM-A2`:

```bash
# On Active Node (LTM-A1):
tmsh run sys failover standby
```

### Verification:
1. Observe that `LTM-A1` changes state to `Standby`.
2. Verify on `LTM-A2` (`10.1.1.21`):
   ```bash
   tmsh show cm failover-status
   ```
   *Expected Result*: `LTM-A2` is now `Active`.
3. Verify that Floating Self-IP `10.1.100.10` and Virtual Servers respond without packet loss:
   ```bash
   ping 10.1.100.10
   curl -k https://10.1.100.50/health
   ```

---

## 4. Forced Unplanned Failure Simulation
To simulate a sudden appliance loss:
1. Log into F5OS-A platform host (`https://10.1.0.10`).
2. Navigate to **Tenants** -> select `ltm-tenant-a1` -> Click **Stop** / Set running state to `Provisioned`.
3. Confirm that `LTM-A2` assumes `Active` state within 300ms via network failover heartbeats on VLAN 900.
4. Restart tenant on F5OS-A and verify it rejoins as `Standby` and resynchronizes configuration.
