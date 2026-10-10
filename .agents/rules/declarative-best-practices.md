# Declarative Best Practices for F5 DO and AS3
# Scope: TMOS Declarative Onboarding (DO) and Application Services 3 (AS3)

## 1. Declarative Golden Rules
- **Idempotency**: All configurations must be declared in target state format. Never use imperative `tmsh` commands in production automation.
- **Strict Schema Validation**: Validate all JSON payloads against the vendored AS3 (v3.50+) and DO (v1.42+) schemas before committing or applying.
- **Tenant Scope Separation**: Application teams are granted AS3 declaration access ONLY within their specific Tenant block. They must never be able to modify the `Common` partition.

## 2. Declarative Onboarding (DO) Standards
- Always configure NTP servers (minimum 3 sources) and DNS forwarders declaratively.
- Establish dedicated non-routable VLANs for ConfigSync and Network Failover heartbeats.
- Device trust and Sync-Failover group configuration must be deployed symmetrically on both nodes of an HA pair.

## 3. AS3 Application Standards
- Group related Virtual Servers, Pools, and Monitors inside a single AS3 `Application` block.
- Always attach a health monitor to pools. Never deploy an unmonitored pool.
- Use explicit HTTP health monitors with `HTTP/1.1` and `Connection: Close` headers.
