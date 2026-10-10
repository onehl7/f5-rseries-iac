"""
F5 iSeries to rSeries Deprecation & Compatibility Analyzer
Scans parsed TMOS configurations for deprecated features, insecure cipher suites,
hardware-specific directives, obsolete iRule patterns, and network interface syntax
incompatible with rSeries F5OS virtual tenants.
"""

import re
from typing import Dict, Any, List


class DeprecationFinding:
    """Represents a specific deprecation or compatibility finding."""

    def __init__(
        self,
        category: str,
        severity: str,
        object_name: str,
        description: str,
        remediation: str,
        source_context: str = ""
    ):
        self.category = category  # SSL_CIPHERS, PROTOCOLS, MONITORS, IRULES, NETWORKING, HARDWARE
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW, INFO
        self.object_name = object_name
        self.description = description
        self.remediation = remediation
        self.source_context = source_context

    def to_dict(self) -> Dict[str, str]:
        return {
            "category": self.category,
            "severity": self.severity,
            "object_name": self.object_name,
            "description": self.description,
            "remediation": self.remediation,
            "source_context": self.source_context,
        }


class DeprecationAnalyzer:
    """Performs deep rule-based inspection across parsed TMOS objects."""

    INSECURE_CIPHER_KEYWORDS = [
        "rc4", "des", "3des", "export", "null", "md5", "compat", "cbc"
    ]

    INSECURE_PROTOCOLS = [
        "sslv2", "sslv3", "tlsv1.0", "tlsv1_0"
    ]

    DEPRECATED_IRULE_COMMANDS = [
        ("matchclass", "Use 'class match' instead of legacy 'matchclass'"),
        ("session add", "Review session table usage; consider modern table command with strict timeouts"),
        ("eval", "Avoid eval in iRules for security and performance"),
        ("findclass", "Use 'class match -value' instead of legacy 'findclass'"),
    ]

    def __init__(self):
        pass

    def analyze(self, parsed_config: Dict[str, Any]) -> List[DeprecationFinding]:
        """Runs all deprecation checks against parsed TMOS catalog."""
        findings: List[DeprecationFinding] = []

        findings.extend(self._check_ssl_profiles(parsed_config.get("ssl_profiles_client", {}), "Client-SSL"))
        findings.extend(self._check_ssl_profiles(parsed_config.get("ssl_profiles_server", {}), "Server-SSL"))
        findings.extend(self._check_monitors(parsed_config.get("monitors", {})))
        findings.extend(self._check_irules(parsed_config.get("irules", {})))
        findings.extend(self._check_networking(parsed_config.get("vlans", {})))
        findings.extend(self._check_hardware_dependencies(parsed_config.get("other", {})))

        return findings

    def _check_ssl_profiles(self, profiles: Dict[str, Any], profile_type: str) -> List[DeprecationFinding]:
        findings = []

        for name, conf in profiles.items():
            ciphers = str(conf.get("ciphers", "")).lower()
            options = str(conf.get("options", "")).lower()

            # Cipher suite audit
            for kw in self.INSECURE_CIPHER_KEYWORDS:
                if kw in ciphers:
                    findings.append(DeprecationFinding(
                        category="SSL_CIPHERS",
                        severity="HIGH" if kw in ["rc4", "des", "3des", "export"] else "MEDIUM",
                        object_name=f"{profile_type}:{name}",
                        description=f"Insecure cipher keyword '{kw}' detected in cipher string: '{ciphers}'.",
                        remediation="Update cipher string to modern secure suites (e.g. 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256' or F5 'DEFAULT').",
                        source_context=f"ciphers {ciphers}"
                    ))

            # COMPAT stack check (iSeries hardware crypto stack not present in TMOS 17.x / rSeries)
            if "compat" in ciphers:
                findings.append(DeprecationFinding(
                    category="HARDWARE_CRYPTO",
                    severity="CRITICAL",
                    object_name=f"{profile_type}:{name}",
                    description="Legacy COMPAT cipher stack detected. COMPAT is deprecated and unsupported on rSeries TMOS 17.x.",
                    remediation="Migrate from COMPAT stack to NATIVE OpenSSL / TLSv1.3 cipher profiles.",
                    source_context=f"ciphers {ciphers}"
                ))

            # Protocol audit
            for proto in self.INSECURE_PROTOCOLS:
                if proto in options or (proto in ciphers and "no-" not in options):
                    findings.append(DeprecationFinding(
                        category="PROTOCOLS",
                        severity="HIGH",
                        object_name=f"{profile_type}:{name}",
                        description=f"Insecure protocol '{proto}' enabled or referenced in SSL profile.",
                        remediation="Disable SSLv2, SSLv3, and TLSv1.0; enforce TLSv1.2 and TLSv1.3 only.",
                        source_context=f"options: {options}"
                    ))

        return findings

    def _check_monitors(self, monitors: Dict[str, Any]) -> List[DeprecationFinding]:
        findings = []

        for name, mon in monitors.items():
            conf = mon.get("config", {})
            send_str = str(conf.get("send", ""))

            # Legacy HTTP/1.0 monitor send string without Host header
            if send_str:
                if "HTTP/1.0" in send_str and "Host:" not in send_str:
                    findings.append(DeprecationFinding(
                        category="MONITORS",
                        severity="MEDIUM",
                        object_name=f"monitor:{name}",
                        description="HTTP/1.0 monitor send string lacks HTTP Host header, causing failures on modern HTTP servers.",
                        remediation="Upgrade monitor send string to HTTP/1.1 with explicit Host header and 'Connection: Close'.",
                        source_context=f"send {send_str}"
                    ))
                elif send_str.strip().startswith('"GET /\\r\\n"') or send_str.strip().startswith('"GET /"'):
                    findings.append(DeprecationFinding(
                        category="MONITORS",
                        severity="HIGH",
                        object_name=f"monitor:{name}",
                        description="Ancient HTTP/0.9 monitor string ('GET /\\r\\n') detected.",
                        remediation="Replace with 'GET /health HTTP/1.1\\r\\nHost: f5monitor.local\\r\\nConnection: Close\\r\\n\\r\\n'.",
                        source_context=f"send {send_str}"
                    ))

        return findings

    def _check_irules(self, irules: Dict[str, Any]) -> List[DeprecationFinding]:
        findings = []

        for name, rule_body in irules.items():
            rule_text = str(rule_body)

            for dep_cmd, rem_msg in self.DEPRECATED_IRULE_COMMANDS:
                if dep_cmd in rule_text:
                    findings.append(DeprecationFinding(
                        category="IRULES",
                        severity="MEDIUM",
                        object_name=f"irule:{name}",
                        description=f"Deprecated iRule command '{dep_cmd}' found in rule definition.",
                        remediation=rem_msg,
                        source_context=f"Matched: {dep_cmd}"
                    ))

        return findings

    def _check_networking(self, vlans: Dict[str, Any]) -> List[DeprecationFinding]:
        findings = []

        for name, vlan_body in vlans.items():
            interfaces = vlan_body.get("interfaces", {})
            # In iSeries, interfaces were physical ports like 1.1, 1.2
            for iface in interfaces.keys() if isinstance(interfaces, dict) else []:
                if re.match(r"^\d+\.\d+$", iface):
                    findings.append(DeprecationFinding(
                        category="NETWORKING",
                        severity="HIGH",
                        object_name=f"vlan:{name}",
                        description=f"VLAN references physical port '{iface}'. rSeries virtual tenants consume virtual interfaces trunked from F5OS-A LAGs, not bare physical ports.",
                        remediation="Remove bare physical interfaces from TMOS VLANs. Map the VLAN tag to tenant vNICs via F5OS-A LAG trunk configuration.",
                        source_context=f"interfaces {iface}"
                    ))

        return findings

    def _check_hardware_dependencies(self, other: Dict[str, Any]) -> List[DeprecationFinding]:
        findings = []

        for stanza_header in other.keys():
            if "sys chassis" in stanza_header or "sys hardware" in stanza_header:
                findings.append(DeprecationFinding(
                    category="HARDWARE",
                    severity="CRITICAL",
                    object_name=stanza_header,
                    description="Physical chassis hardware stanza detected in TMOS configuration.",
                    remediation="Chassis management is handled exclusively by F5OS-A on rSeries. Remove chassis stanzas from TMOS declarations.",
                    source_context=stanza_header
                ))

        return findings
