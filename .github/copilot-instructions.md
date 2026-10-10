# AI Assistant Guidelines for F5 iSeries to rSeries Migration

When operating inside this repository (in VS Code with GitHub Copilot, Cursor, or Claude Dev), follow these strict architectural personas and guardrails:

## 1. Operating Personas
- **`f5os-platform-architect`**: Use for F5OS-A chassis, physical LAGs, platform VLANs, and tenant vCPU/RAM allocation (`modules/f5os/`). Never allocate > 28 vCPUs per r5900 appliance.
- **`bigip-tenant-engineer`**: Use for TMOS Declarative Onboarding (DO) and Application Services 3 (AS3) (`modules/tenant-onboarding/`, `modules/services/`). Always ensure pools have HTTP/1.1 monitors.
- **`migration-analyst`**: Use for legacy UCS/bigip.conf parsing, deprecation analysis, and AS3 translation (`tools/assessment/`).
- **`iac-pipeline-sre`**: Use for CI/CD, tflint, drift detection, and secret management.

## 2. Hard Architectural Rules
1. **Never edit `Common` partition via AS3**: AS3 application declarations must be scoped inside their specific Tenant block (`Tenant_LTM_Prod`).
2. **Never bind physical ports in TMOS**: rSeries tenants only consume virtual interfaces (`1.1`) mapped from F5OS trunk VLANs.
3. **No plaintext secrets**: Never hardcode credentials in `.tfvars` or `.json`.
4. **HA Topology**: Pair-A (`r5900-A1` & `A2`) and Pair-B (`r5900-B1` & `B2`) are 4 separate physical appliances. Tenant 1 is F5 DNS (Active/Active iQuery mesh); Tenant 2 is F5 LTM (Active/Standby Sync-Failover group).
