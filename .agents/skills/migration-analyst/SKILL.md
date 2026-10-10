---
name: migration-analyst
description: Performs legacy F5 iSeries UCS and bigip.conf ingestion, deprecation analysis, hardware sizing translation, and AS3/GSLB declaration synthesis.
---

# Migration Analyst Skill

## Objective
Analyze, parse, audit, and transform legacy iSeries configurations into valid declarative AS3 and GSLB schemas for the target 4x r5900 multi-tenant deployment.

## Key Responsibilities
1. **Source Ingestion**:
   - Extract UCS archives and parse `bigip.conf` stanzas into AST representations via `tools/assessment/conf_parser.py`.
2. **Deprecation Audit**:
   - Identify unsupported hardware offload directives (e.g. `COMPAT` cipher stack), insecure ciphers, and physical interface references via `tools/assessment/deprecation_analyzer.py`.
3. **Capacity Planning**:
   - Calculate r5900 tenant sizing (vCPU and RAM) to guarantee adequate headroom and prevent chassis overcommitment via `tools/assessment/sizing_calculator.py`.
4. **Declarative Synthesis**:
   - Auto-generate valid AS3 v3.50+ declarations and GSLB data structures via `tools/assessment/as3_converter.py` and `gtm_converter.py`.
