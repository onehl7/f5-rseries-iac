#!/usr/bin/env python3
"""
F5 iSeries to rSeries Migration Assessment CLI
Executes parsing, deprecation analysis, r5900 multi-tenant capacity sizing,
and declarative AS3/GSLB translation.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

from conf_parser import TMOSConfParser
from deprecation_analyzer import DeprecationAnalyzer
from sizing_calculator import R5900SizingCalculator
from as3_converter import AS3Converter
from gtm_converter import GTMConverter
from ucs_extractor import UCSExtractor


def run_assessment(
    config_file: str,
    legacy_model: str = "i5800",
    output_dir: str = "./assessment_output",
    tenant_name: str = "Tenant_LTM_Prod"
) -> Dict[str, Any]:
    """Runs the complete 4-stage assessment workflow."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting assessment for: {config_file}")
    print(f"[*] Source legacy appliance model: {legacy_model}")

    # Step 1: Configuration Ingestion & Parsing
    parser = TMOSConfParser()
    if config_file.endswith(".ucs") or config_file.endswith(".tar.gz"):
        print(f"[*] Unpacking UCS archive...")
        with UCSExtractor(config_file) as extractor:
            extracted = extractor.extract()
            main_conf = extracted.get("config/bigip.conf")
            if not main_conf:
                raise FileNotFoundError("config/bigip.conf not found inside UCS archive.")
            parsed_catalog = parser.parse_file(str(main_conf))
    else:
        parsed_catalog = parser.parse_file(config_file)

    vs_count = len(parsed_catalog.get("virtual_servers", {}))
    pool_count = len(parsed_catalog.get("pools", {}))
    node_count = len(parsed_catalog.get("nodes", {}))
    wip_count = len(parsed_catalog.get("gtm_wideips", {}))
    print(f"[+] Parsed {vs_count} Virtual Servers, {pool_count} Pools, {node_count} Nodes, {wip_count} GTM WideIPs.")

    # Step 2: Compatibility & Deprecation Analysis
    analyzer = DeprecationAnalyzer()
    findings = analyzer.analyze(parsed_catalog)
    findings_by_severity = {
        "CRITICAL": [f.to_dict() for f in findings if f.severity == "CRITICAL"],
        "HIGH": [f.to_dict() for f in findings if f.severity == "HIGH"],
        "MEDIUM": [f.to_dict() for f in findings if f.severity == "MEDIUM"],
        "LOW": [f.to_dict() for f in findings if f.severity == "LOW"],
    }
    print(f"[+] Deprecation audit completed: {len(findings)} total findings "
          f"({len(findings_by_severity['CRITICAL'])} Critical, {len(findings_by_severity['HIGH'])} High).")

    # Step 3: r5900 Multi-Tenant Sizing Evaluation
    sizer = R5900SizingCalculator()
    sizing_report = sizer.evaluate_migration(legacy_model=legacy_model)
    print(f"[+] r5900 Multi-Tenant sizing status: {sizing_report['performance_validation']['status']} "
          f"(Headroom: {sizing_report['per_chassis_allocation']['headroom_pct']}%)")

    # Step 4: Declarative Translation
    as3_conv = AS3Converter(tenant_name=tenant_name)
    as3_payload = as3_conv.convert(parsed_catalog)

    gtm_conv = GTMConverter()
    gtm_payload = gtm_conv.convert(parsed_catalog)

    # Output Artifacts
    # 1. AS3 JSON
    as3_file = out_path / "as3_declaration_output.json"
    with open(as3_file, "w", encoding="utf-8") as f:
        json.dump(as3_payload, f, indent=2)

    # 2. GTM JSON
    gtm_file = out_path / "gslb_declaration_output.json"
    with open(gtm_file, "w", encoding="utf-8") as f:
        json.dump(gtm_payload, f, indent=2)

    # 3. Inventory & Assessment JSON
    inventory_data = {
        "source_config": config_file,
        "legacy_model": legacy_model,
        "parsed_inventory_summary": {
            "virtual_servers": vs_count,
            "pools": pool_count,
            "nodes": node_count,
            "gtm_wideips": wip_count,
            "ssl_profiles_client": len(parsed_catalog.get("ssl_profiles_client", {})),
            "ssl_profiles_server": len(parsed_catalog.get("ssl_profiles_server", {})),
            "irules": len(parsed_catalog.get("irules", {})),
        },
        "sizing_budget_r5900": sizing_report,
        "deprecation_findings": findings_by_severity,
    }
    inv_file = out_path / "migration_inventory.json"
    with open(inv_file, "w", encoding="utf-8") as f:
        json.dump(inventory_data, f, indent=2)

    # 4. Markdown Assessment Report
    report_file = out_path / "migration_assessment_report.md"
    _generate_markdown_report(report_file, inventory_data)

    print(f"[✔] Assessment complete! Artifacts written to: {out_path.resolve()}")
    return inventory_data


def _generate_markdown_report(report_path: Path, data: Dict[str, Any]):
    """Renders executive Markdown audit report."""
    inv = data["parsed_inventory_summary"]
    sizing = data["sizing_budget_r5900"]
    findings = data["deprecation_findings"]

    md_lines = [
        "# F5 iSeries to rSeries (4x r5900) Migration Assessment Report",
        "",
        "## 1. Executive Summary",
        f"- **Source Config**: `{data['source_config']}`",
        f"- **Source Legacy Model**: `{data['legacy_model']}`",
        f"- **Target Architecture**: **4x F5 r5900 Appliances** in 2 Physical Pairs (`Pair-A` & `Pair-B`)",
        f"- **Tenant Topology per Chassis**: Tenant 1 (DNS Anycast Mesh, 4 vCPUs) & Tenant 2 (LTM Active/Standby HA, 16 vCPUs)",
        f"- **Capacity Validation**: **{sizing['performance_validation']['status']}** ({sizing['per_chassis_allocation']['headroom_pct']}% Chassis Headroom)",
        "",
        "## 2. Inventory Summary",
        "| Object Category | Discovered Count | Migration Strategy |",
        "| :--- | :--- | :--- |",
        f"| Virtual Servers | {inv['virtual_servers']} | Transformed to AS3 `Service_HTTP` / `Service_HTTPS` |",
        f"| Pools & Members | {inv['pools']} | Transformed to AS3 `Pool` declarations |",
        f"| Backend Nodes | {inv['nodes']} | Declared as AS3 pool member endpoints |",
        f"| GTM WideIPs | {inv['gtm_wideips']} | Transformed to Declarative GSLB WideIP definitions |",
        f"| Client-SSL Profiles | {inv['ssl_profiles_client']} | Migrated to AS3 `TLS_Server` profiles |",
        f"| iRules | {inv['irules']} | Preserved and referenced in AS3 Application blocks |",
        "",
        "## 3. Deprecation & Compatibility Audit",
        f"- **Critical Findings**: {len(findings['CRITICAL'])}",
        f"- **High Severity**: {len(findings['HIGH'])}",
        f"- **Medium Severity**: {len(findings['MEDIUM'])}",
        "",
    ]

    if findings["CRITICAL"] or findings["HIGH"]:
        md_lines.extend([
            "### Actionable High & Critical Findings",
            "| Severity | Category | Object | Issue Description | Remediation |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ])
        for f in findings["CRITICAL"] + findings["HIGH"]:
            desc = f['description'].replace("|", "/")
            rem = f['remediation'].replace("|", "/")
            md_lines.append(f"| **{f['severity']}** | {f['category']} | `{f['object_name']}` | {desc} | {rem} |")
        md_lines.append("")

    md_lines.extend([
        "## 4. r5900 Resource Allocation Budget",
        "| Resource Component | Allocated vCPUs | Allocated RAM | High Availability Protocol |",
        "| :--- | :--- | :--- | :--- |",
        f"| F5OS-A Host Platform | {sizing['per_chassis_allocation']['f5os_host_vcpus']} vCPUs | {sizing['per_chassis_allocation']['f5os_host_ram_gb']} GB | Redundant Chassis Hardware |",
        f"| Tenant 1: F5 DNS | {sizing['per_chassis_allocation']['tenant_1_dns_vcpus']} vCPUs | {sizing['per_chassis_allocation']['tenant_1_dns_ram_gb']} GB | Active/Active iQuery Anycast Mesh |",
        f"| Tenant 2: F5 LTM | {sizing['per_chassis_allocation']['tenant_2_ltm_vcpus']} vCPUs | {sizing['per_chassis_allocation']['tenant_2_ltm_ram_gb']} GB | Active/Standby Sync-Failover HA Pair |",
        f"| Free Safety Buffer | {sizing['per_chassis_allocation']['free_headroom_vcpus']} vCPUs | {sizing['per_chassis_allocation']['free_headroom_ram_gb']} GB | Available for Burst / Growth |",
        "",
        "## 5. Generated Declarative Artifacts",
        "- **AS3 LTM Declaration**: `as3_declaration_output.json`",
        "- **GSLB DNS Declaration**: `gslb_declaration_output.json`",
        "- **Raw Inventory & Audit**: `migration_inventory.json`",
    ])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="F5 iSeries to rSeries Assessment Tool")
    parser.add_argument("--config", "-c", required=True, help="Path to bigip.conf or UCS archive")
    parser.add_argument("--model", "-m", default="i5800", help="Legacy iSeries model (i2800, i5800, i7800, i10800)")
    parser.add_argument("--output", "-o", default="./assessment_output", help="Output directory for reports & AS3")
    parser.add_argument("--tenant", "-t", default="Tenant_LTM_Prod", help="Target AS3 tenant name")

    args = parser.parse_args()
    run_assessment(
        config_file=args.config,
        legacy_model=args.model,
        output_dir=args.output,
        tenant_name=args.tenant
    )
