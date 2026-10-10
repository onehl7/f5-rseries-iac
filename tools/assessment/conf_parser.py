"""
TMOS Configuration Parser (AST / Lexer)
Parses F5 BIG-IP bigip.conf and bigip_gtm.conf hierarchical stanzas into structured Python dictionaries.
Supports LTM Virtuals, Pools, Nodes, Monitors, SSL Profiles, Persistence Profiles, iRules, and GTM WideIPs.
"""

import re
from typing import Dict, Any, List, Tuple, Optional


class TMOSConfParser:
    """Tokenizes and parses TMOS hierarchical configuration files."""

    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Reads and parses a bigip.conf file from disk."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return self.parse_string(content)

    def parse_string(self, content: str) -> Dict[str, Any]:
        """Parses a string containing TMOS configuration stanzas into a structured object."""
        cleaned_content = self._strip_comments(content)
        tokens = self._tokenize(cleaned_content)
        parsed_root, _ = self._parse_block(tokens, 0)
        return self._categorize_stanzas(parsed_root)

    def _strip_comments(self, text: str) -> str:
        """Removes TMOS comment lines starting with # while preserving quoted strings."""
        lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            lines.append(line)
        return "\n".join(lines)

    def _tokenize(self, text: str) -> List[str]:
        """Splits configuration into syntactic tokens: words, quoted strings, braces, and newlines."""
        pattern = r'\{|\}|\n|"[^"\\]*(?:\\.[^"\\]*)*"|[^\s\{\}]+'
        tokens = re.findall(pattern, text)
        return tokens

    def _parse_block(self, tokens: List[str], index: int) -> Tuple[Dict[str, Any], int]:
        """Recursively parses tokens between { and } into key-value mappings and sub-blocks."""
        result: Dict[str, Any] = {}
        header_tokens: List[str] = []

        while index < len(tokens):
            token = tokens[index]

            if token == "\n":
                if header_tokens:
                    line_val = " ".join(header_tokens).strip()
                    if line_val:
                        self._add_attribute(result, line_val)
                    header_tokens = []
                index += 1
                continue

            if token == "{":
                block_key = " ".join(header_tokens).strip()
                header_tokens = []
                sub_block, next_index = self._parse_block(tokens, index + 1)
                index = next_index

                if block_key in result:
                    # If multiple blocks share key, convert to list
                    if isinstance(result[block_key], list):
                        result[block_key].append(sub_block)
                    else:
                        result[block_key] = [result[block_key], sub_block]
                else:
                    result[block_key] = sub_block

            elif token == "}":
                # Close current block
                if header_tokens:
                    line_val = " ".join(header_tokens).strip()
                    if line_val:
                        self._add_attribute(result, line_val)
                return result, index + 1

            else:
                header_tokens.append(token)
                index += 1

        if header_tokens:
            line_val = " ".join(header_tokens).strip()
            if line_val:
                self._add_attribute(result, line_val)

        return result, index

    def _add_attribute(self, current_dict: Dict[str, Any], statement: str):
        """Processes flat key-value statements like 'destination 10.1.1.50:443' or 'address 10.1.1.20'."""
        parts = statement.strip().split(None, 1)
        if len(parts) == 2:
            key, val = parts[0], parts[1].strip('"')
            current_dict[key] = val
        elif len(parts) == 1:
            current_dict[parts[0]] = True

    def _categorize_stanzas(self, raw_tree: Dict[str, Any]) -> Dict[str, Any]:
        """Organizes raw top-level stanzas into clear TMOS object categories."""
        catalog: Dict[str, Dict[str, Any]] = {
            "virtual_servers": {},
            "pools": {},
            "nodes": {},
            "monitors": {},
            "ssl_profiles_client": {},
            "ssl_profiles_server": {},
            "http_profiles": {},
            "irules": {},
            "persistence_profiles": {},
            "gtm_wideips": {},
            "gtm_pools": {},
            "gtm_servers": {},
            "gtm_datacenters": {},
            "vlans": {},
            "self_ips": {},
            "other": {},
        }

        for stanza_header, body in raw_tree.items():
            parts = stanza_header.split()
            if not parts:
                continue

            main_cmd = parts[0]

            if main_cmd == "ltm":
                sub_cmd = parts[1] if len(parts) > 1 else ""
                obj_name = parts[-1] if len(parts) > 2 else (parts[1] if len(parts) > 1 else "unnamed")

                clean_name = obj_name.split("/")[-1]

                if sub_cmd == "virtual":
                    catalog["virtual_servers"][clean_name] = self._normalize_virtual(obj_name, body)
                elif sub_cmd == "pool":
                    catalog["pools"][clean_name] = self._normalize_pool(obj_name, body)
                elif sub_cmd == "node":
                    catalog["nodes"][clean_name] = self._normalize_node(obj_name, body)
                elif sub_cmd == "monitor":
                    monitor_type = parts[2] if len(parts) > 3 else "custom"
                    catalog["monitors"][clean_name] = {"type": monitor_type, "config": body}
                elif sub_cmd == "profile" and len(parts) > 3:
                    prof_type = parts[2]
                    if prof_type == "client-ssl":
                        catalog["ssl_profiles_client"][clean_name] = body
                    elif prof_type == "server-ssl":
                        catalog["ssl_profiles_server"][clean_name] = body
                    elif prof_type == "http":
                        catalog["http_profiles"][clean_name] = body
                    elif "persist" in prof_type:
                        catalog["persistence_profiles"][clean_name] = body
                    else:
                        catalog["other"][stanza_header] = body
                elif sub_cmd == "rule":
                    catalog["irules"][clean_name] = body
                else:
                    catalog["other"][stanza_header] = body

            elif main_cmd == "gtm":
                sub_cmd = parts[1] if len(parts) > 1 else ""
                obj_name = parts[-1] if len(parts) > 2 else "unnamed"
                clean_name = obj_name.split("/")[-1]

                if sub_cmd == "wideip":
                    catalog["gtm_wideips"][clean_name] = body
                elif sub_cmd == "pool":
                    catalog["gtm_pools"][clean_name] = body
                elif sub_cmd == "server":
                    catalog["gtm_servers"][clean_name] = body
                elif sub_cmd == "datacenter":
                    catalog["gtm_datacenters"][clean_name] = body
                else:
                    catalog["other"][stanza_header] = body

            elif main_cmd == "net":
                sub_cmd = parts[1] if len(parts) > 1 else ""
                obj_name = parts[-1] if len(parts) > 2 else "unnamed"
                clean_name = obj_name.split("/")[-1]
                if sub_cmd == "vlan":
                    catalog["vlans"][clean_name] = body
                elif sub_cmd == "self":
                    catalog["self_ips"][clean_name] = body
                else:
                    catalog["other"][stanza_header] = body
            else:
                catalog["other"][stanza_header] = body

        return catalog

    def _normalize_virtual(self, name: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes virtual server attributes for downstream transformation."""
        destination = body.get("destination", "")
        # Format can be /Common/10.1.1.10:443 or 10.1.1.10:https
        ip = ""
        port = ""
        if destination:
            clean_dest = destination.split("/")[-1]
            if ":" in clean_dest:
                ip, port = clean_dest.split(":", 1)
            else:
                ip = clean_dest

        # Extract profiles list
        profiles = []
        raw_profiles = body.get("profiles", {})
        if isinstance(raw_profiles, dict):
            profiles = list(raw_profiles.keys())
        elif isinstance(raw_profiles, list):
            profiles = raw_profiles

        # Extract pool
        pool = body.get("pool", "")

        # Extract rules
        rules = []
        raw_rules = body.get("rules", {})
        if isinstance(raw_rules, dict):
            rules = list(raw_rules.keys())
        elif isinstance(raw_rules, str):
            rules = [raw_rules]

        return {
            "name": name,
            "destination": destination,
            "ip": ip,
            "port": port,
            "pool": pool,
            "profiles": profiles,
            "rules": rules,
            "raw": body,
        }

    def _normalize_pool(self, name: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes pool members and monitor configuration."""
        members = []
        raw_members = body.get("members", {})
        if isinstance(raw_members, dict):
            for m_key, m_val in raw_members.items():
                m_clean = m_key.split("/")[-1]
                m_node_name, m_port = m_clean.split(":", 1) if ":" in m_clean else (m_clean, "0")
                member_addr = m_node_name
                if isinstance(m_val, dict) and "address" in m_val:
                    member_addr = m_val["address"]
                members.append({
                    "name": m_clean,
                    "node_name": m_node_name,
                    "ip": member_addr,
                    "port": m_port,
                    "state": m_val.get("session", "user-enabled") if isinstance(m_val, dict) else "user-enabled"
                })

        monitor = body.get("monitor", "")
        lb_method = body.get("load-balancing-mode", "round-robin")

        return {
            "name": name,
            "members": members,
            "monitor": monitor,
            "load_balancing_mode": lb_method,
            "raw": body,
        }

    def _normalize_node(self, name: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes node address."""
        address = body.get("address", name.split("/")[-1])
        return {
            "name": name,
            "address": address,
            "raw": body,
        }
