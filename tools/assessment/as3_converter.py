"""
F5 Application Services 3 (AS3) Translation Engine
Transforms parsed legacy iSeries TMOS LTM objects (Virtual Servers, Pools, Monitors, SSL Profiles)
into production-ready declarative AS3 v3.50+ JSON declarations.
"""

import json
import re
from typing import Dict, Any, List, Optional


class AS3Converter:
    """Converts parsed TMOS configuration into F5 AS3 declarative JSON."""

    SCHEMA_URL = "https://raw.githubusercontent.com/F5Networks/f5-appsvcs-extension/master/schema/latest/as3-schema.json"

    def __init__(self, tenant_name: str = "Tenant_LTM_Prod"):
        self.tenant_name = tenant_name

    def convert(self, parsed_catalog: Dict[str, Any]) -> Dict[str, Any]:
        """Generates full AS3 declaration envelope from parsed TMOS catalog."""
        declaration: Dict[str, Any] = {
            "class": "ADC",
            "schemaVersion": "3.50.0",
            "id": f"urn:f5:rseries:{self.tenant_name.lower()}:migration",
            "label": "Migrated LTM Application Services",
            "remark": "Auto-converted from legacy F5 iSeries bigip.conf by Antigravity Assessment Engine",
            self.tenant_name: {
                "class": "Tenant"
            }
        }

        tenant_body = declaration[self.tenant_name]
        virtual_servers = parsed_catalog.get("virtual_servers", {})
        pools = parsed_catalog.get("pools", {})
        nodes = parsed_catalog.get("nodes", {})
        monitors = parsed_catalog.get("monitors", {})
        client_ssl_profiles = parsed_catalog.get("ssl_profiles_client", {})

        # Group virtual servers into AS3 Applications
        for vs_name, vs_info in virtual_servers.items():
            clean_app_name = self._sanitize_name(vs_name)
            app_declaration = self._build_application(
                clean_app_name, vs_info, pools, nodes, monitors, client_ssl_profiles
            )
            tenant_body[clean_app_name] = app_declaration

        return {
            "$schema": self.SCHEMA_URL,
            "class": "AS3",
            "action": "deploy",
            "persist": True,
            "declaration": declaration
        }

    def _build_application(
        self,
        app_name: str,
        vs_info: Dict[str, Any],
        all_pools: Dict[str, Any],
        all_nodes: Dict[str, Any],
        all_monitors: Dict[str, Any],
        all_client_ssl: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Constructs an individual AS3 Application object."""
        app_obj: Dict[str, Any] = {
            "class": "Application",
            "template": "generic"
        }

        vip_ip = vs_info.get("ip", "0.0.0.0")
        raw_port = vs_info.get("port", "443")
        port_num = 443 if raw_port in ["443", "https"] else (80 if raw_port in ["80", "http"] else int(raw_port) if raw_port.isdigit() else 443)

        # Check if SSL profile attached
        has_client_ssl = False
        ssl_profile_name = None
        for prof in vs_info.get("profiles", []):
            clean_p = prof.split("/")[-1]
            if clean_p in all_client_ssl or "clientssl" in clean_p.lower() or "ssl" in clean_p.lower():
                has_client_ssl = True
                ssl_profile_name = clean_p
                break

        service_name = f"service_{app_name}"
        service_class = "Service_HTTPS" if has_client_ssl or port_num == 443 else "Service_HTTP"

        service_def: Dict[str, Any] = {
            "class": service_class,
            "virtualAddresses": [vip_ip],
            "virtualPort": port_num,
        }

        # Associate pool
        raw_pool = vs_info.get("pool", "")
        if raw_pool:
            clean_pool = self._sanitize_name(raw_pool)
            service_def["pool"] = clean_pool

            # Construct Pool definition if found in catalog
            pool_data = all_pools.get(raw_pool.split("/")[-1]) or all_pools.get(raw_pool)
            if pool_data:
                app_obj[clean_pool] = self._build_pool(clean_pool, pool_data, all_nodes, all_monitors, app_obj)

        # Associate TLS if HTTPS
        if service_class == "Service_HTTPS":
            tls_obj_name = f"tls_{app_name}"
            service_def["serverTLS"] = tls_obj_name
            app_obj[tls_obj_name] = {
                "class": "TLS_Server",
                "certificates": [
                    {
                        "certificate": f"cert_{app_name}"
                    }
                ]
            }
            # Certificate placeholder declaration
            app_obj[f"cert_{app_name}"] = {
                "class": "Certificate",
                "remark": f"Migrated TLS certificate reference for {app_name}. Replace with Vault / cert store reference.",
                "certificate": {
                    "bigip": f"/Common/{ssl_profile_name or 'default'}.crt"
                }
            }

        app_obj[service_name] = service_def
        return app_obj

    def _build_pool(
        self,
        pool_name: str,
        pool_info: Dict[str, Any],
        all_nodes: Dict[str, Any],
        all_monitors: Dict[str, Any],
        parent_app: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Constructs an AS3 Pool object with its members and monitors."""
        lb_mode = pool_info.get("load_balancing_mode", "round-robin").replace("-", "-")
        members_list = []

        # Group members by port
        port_to_ips: Dict[int, List[str]] = {}
        for m in pool_info.get("members", []):
            m_ip = m.get("ip", "")
            # If m_ip is not a pure IP, try resolving from all_nodes
            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", m_ip):
                node_clean = m.get("node_name", m_ip)
                node_match = all_nodes.get(node_clean) or all_nodes.get(f"/Common/{node_clean}")
                if node_match and "address" in node_match:
                    m_ip = node_match["address"]

            m_port = int(m.get("port", "80")) if str(m.get("port", "")).isdigit() else 80
            if m_ip:
                port_to_ips.setdefault(m_port, []).append(m_ip)

        for port, ips in port_to_ips.items():
            members_list.append({
                "servicePort": port,
                "serverAddresses": ips
            })

        pool_def: Dict[str, Any] = {
            "class": "Pool",
            "loadBalancingMode": lb_mode,
            "members": members_list
        }

        # Monitor handling
        raw_mon = pool_info.get("monitor", "")
        if raw_mon:
            clean_mon = self._sanitize_name(raw_mon)
            pool_def["monitors"] = [{"use": clean_mon}]

            # Add monitor definition if present
            mon_data = all_monitors.get(raw_mon.split("/")[-1])
            if mon_data:
                conf = mon_data.get("config", {})
                parent_app[clean_mon] = {
                    "class": "Monitor",
                    "monitorType": "http" if "http" in mon_data.get("type", "") else "tcp",
                    "interval": int(conf.get("interval", 5)),
                    "timeout": int(conf.get("timeout", 16)),
                }
                if conf.get("send"):
                    parent_app[clean_mon]["send"] = conf["send"].strip('"')
                if conf.get("recv"):
                    parent_app[clean_mon]["receive"] = conf["recv"].strip('"')
            else:
                # Default monitor fallback
                pool_def["monitors"] = ["http"]

        return pool_def

    def _sanitize_name(self, name: str) -> str:
        """Sanitizes TMOS object names into valid AS3 identifier strings."""
        clean = name.split("/")[-1]
        clean = re.sub(r"[^a-zA-Z0-9_]", "_", clean)
        return clean.strip("_")
