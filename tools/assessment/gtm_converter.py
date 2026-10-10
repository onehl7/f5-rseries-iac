"""
F5 BIG-IP DNS (GTM) Translation Engine
Transforms parsed legacy iSeries GTM WideIPs, GTM Pools, and Data Centers
into declarative DNS configurations tailored for the Tenant 1 (DNS) active/active iQuery mesh on r5900.
"""

from typing import Dict, Any, List


class GTMConverter:
    """Converts legacy GTM / BIG-IP DNS configuration into declarative data structures."""

    def __init__(self):
        pass

    def convert(self, parsed_catalog: Dict[str, Any]) -> Dict[str, Any]:
        """Processes GTM WideIPs and pools into structured declarative declarations."""
        wideips = parsed_catalog.get("gtm_wideips", {})
        gtm_pools = parsed_catalog.get("gtm_pools", {})
        gtm_datacenters = parsed_catalog.get("gtm_datacenters", {})
        gtm_servers = parsed_catalog.get("gtm_servers", {})

        converted_wideips: List[Dict[str, Any]] = []

        for wip_name, wip_body in wideips.items():
            clean_name = wip_name.split("/")[-1]
            pools_associated = []

            # Extract associated pools
            raw_pools = wip_body.get("pools", {})
            if isinstance(raw_pools, dict):
                pools_associated = [p.split("/")[-1] for p in raw_pools.keys()]
            elif isinstance(raw_pools, list):
                pools_associated = [p.split("/")[-1] for p in raw_pools]

            converted_wideips.append({
                "fqdn": clean_name,
                "record_type": "A",
                "pools": pools_associated,
                "load_balancing_decision_log": True,
            })

        # Format datacenters for Pair-A and Pair-B
        target_datacenters = [
            {"name": "DC1_PairA", "location": "Primary Site - Pair-A (r5900-A1, r5900-A2)"},
            {"name": "DC2_PairB", "location": "Secondary Site - Pair-B (r5900-B1, r5900-B2)"},
        ]

        # Format servers representation (iQuery servers linking LTM tenants to DNS tenants)
        iquery_mesh_servers = [
            {
                "name": "r5900_PairA_LTM_Cluster",
                "datacenter": "DC1_PairA",
                "product": "bigip",
                "devices": ["10.1.1.20", "10.1.1.21"],  # LTM-A1 & LTM-A2
                "description": "LTM Tenant HA Pair in Pair-A reporting VIP health via iQuery"
            },
            {
                "name": "r5900_PairB_LTM_Cluster",
                "datacenter": "DC2_PairB",
                "product": "bigip",
                "devices": ["10.2.1.20", "10.2.1.21"],  # LTM-B1 & LTM-B2
                "description": "LTM Tenant HA Pair in Pair-B reporting VIP health via iQuery"
            }
        ]

        return {
            "gslb_schema_version": "1.0.0",
            "target_architecture": "Active/Active iQuery Anycast Mesh (Pair-A & Pair-B)",
            "datacenters": target_datacenters,
            "iquery_servers": iquery_mesh_servers,
            "wideips": converted_wideips,
            "legacy_gtm_pool_count": len(gtm_pools),
            "legacy_wideip_count": len(converted_wideips),
        }
