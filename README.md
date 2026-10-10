# F5 iSeries to rSeries (4x r5900) Infrastructure as Code (IaC) Platform

A production-grade, modular Infrastructure as Code (IaC) repository for automating **F5 rSeries** appliance provisioning and migrating legacy **F5 iSeries** TMOS configurations.

---

## Architecture Summary

- **Hardware Footprint**: 4 physical F5 r5900 appliances arranged into 2 physical pairs:
  - **Pair-A (Data Center 1)**: `r5900-A1` and `r5900-A2`
  - **Pair-B (Data Center 2)**: `r5900-B1` and `r5900-B2`
- **Multi-Tenant Topology per Appliance**:
  - **Tenant 1 (F5 DNS)**: Active/Active GSLB query engine operating in an iQuery (TCP 4353) mesh across all 4 appliances with BGP Anycast listener IPs. (4 vCPUs, 16 GB RAM)
  - **Tenant 2 (F5 LTM)**: Dedicated Active/Standby Sync-Failover HA pairs within each physical pair. (16 vCPUs, 48 GB RAM)
- **Decoupled 3-Layer Automation**:
  - **Layer 1: F5OS-A Host**: Physical chassis, LACP LAGs, platform VLANs, and tenant lifecycle (`modules/f5os/`).
  - **Layer 2: Tenant Base**: Declarative Onboarding (DO) for Self-IPs, floating IPs, route domains, and HA clustering (`modules/tenant-onboarding/`).
  - **Layer 3: Application Delivery**: Application Services 3 (AS3) for Virtual Servers, Pools, TLS profiles, and WAF (`modules/services/`).

---

## Directory Organization

```
├── .agents/
│   ├── rules/                       # F5OS guardrails, declarative standards, multi-tenancy rules
│   └── skills/                      # f5os-platform-architect, bigip-tenant-engineer, migration-analyst, iac-pipeline-sre
├── .github/workflows/               # CI/CD: lint-and-validate, drift-detection, deploy-tenant
├── docs/                            # architecture.md, migration-runbook.md, ltm-ha-runbook.md, dns-iquery-mesh.md
├── environments/
│   └── prod/
│       ├── chassis/                 # Pair-A and Pair-B F5OS chassis configurations
│       └── tenants/                 # Pair-A and Pair-B LTM (onboarding/app-services) & DNS stacks
├── modules/
│   ├── f5os/                        # lag, vlan, tenant modules
│   ├── tenant-onboarding/           # do-base, do-networking, do-ha-pair, do-dns-node
│   └── services/                    # as3-http-app, as3-tcp-app, as3-waf-policy
├── tests/
│   ├── fixtures/                    # legacy_iseries_bigip.conf
│   └── unit/                        # Python unit test suite
└── tools/
    └── assessment/                  # ucs_extractor, conf_parser, deprecation_analyzer, sizing_calculator, as3_converter
```

---

## Quickstart

### 1. Run Migration Assessment against Legacy Config
```bash
python3 tools/assessment/run_assessment.py \
  --config tests/fixtures/legacy_iseries_bigip.conf \
  --model i5800 \
  --output ./assessment_output/
```

### 2. Run Test Suite
```bash
make test
```

### 3. Deploy Platform Layer (Pair-A)
```bash
cd environments/prod/chassis/pair-a
terraform init
terraform plan
terraform apply
```

### 4. Deploy LTM HA Pair Onboarding (Pair-A)
```bash
cd environments/prod/tenants/pair-a/ltm/onboarding
terraform init
terraform apply
```

### 5. Deploy AS3 Application Services (Pair-A)
```bash
cd environments/prod/tenants/pair-a/ltm/app-services
terraform init
terraform apply
```

---

## Tool & IDE Integration

### 1. Using with Google Antigravity
Antigravity automatically discovers the skills and rules located in `.agents/`:
- **Context-Aware Activation**: Mentioning "F5OS", "DO onboarding", "AS3", or "UCS assessment" automatically loads the relevant specialist skill (`f5os-platform-architect`, `bigip-tenant-engineer`, `migration-analyst`, or `iac-pipeline-sre`).
- **Explicit Invocations**: You can prompt specific personas directly (e.g., *"As `migration-analyst`, assess `legacy.ucs` and generate the AS3 declaration"*).
- **Rule Enforcement**: The agent is bounded by guardrails in `.agents/rules/` preventing chassis vCPU overcommit and insecure TMOS directives.

### 2. Using with Visual Studio Code (VS Code)
This repository includes full native support for VS Code:
- **Built-in Tasks (`.vscode/tasks.json`)**: Press `Cmd+Shift+B` (or `Ctrl+Shift+B`) to run the assessment engine, unit tests, or Terraform plans directly without typing CLI commands.
- **Recommended Extensions (`.vscode/extensions.json`)**: Includes the official **F5 Extension for VS Code (`f5devcentral.vscode-f5`)**, **HashiCorp Terraform**, and **Python**.
- **JSON Schema Linting (`.vscode/settings.json`)**: AS3 and DO declarations are validated in real-time against official F5 schemas with autocomplete.
- **AI Assistants in VS Code (`.github/copilot-instructions.md` & `.cursorrules`)**: When using GitHub Copilot Chat or Cursor, the AI adheres to the same 4 personas and architectural guardrails.

---

## Documentation Links
- [AI Chat Prompt Playbook (Antigravity & VS Code)](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/ai-chat-prompt-guide.md)
- [Day-0 Hardware & Network Pre-requisites](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/hardware-commissioning-prerequisites.md)
- [Remote State Management & Locking Guide](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/remote-state-management.md)
- [Architecture Blueprint](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/architecture.md)
- [Side-by-Side Migration Runbook](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/migration-runbook.md)
- [VS Code Developer Guide](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/vscode-developer-guide.md)
- [LTM HA Failover Runbook](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/ltm-ha-runbook.md)
- [DNS iQuery Mesh Guide](file:///Users/hl/Documents/antigravity/IaC%20F5/docs/dns-iquery-mesh.md)

