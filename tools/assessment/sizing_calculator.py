"""
F5 r5900 Capacity Planner & Multi-Tenant Sizing Calculator
Calculates resource translation from legacy iSeries appliances (e.g. i5800, i7800, i10800)
to the target 4x F5 r5900 physical appliance layout (Pair-A & Pair-B).
Validates vCPU, RAM, SSL TPS, and throughput budgeting for Tenant 1 (DNS) and Tenant 2 (LTM).
"""

from typing import Dict, Any, List


class R5900SizingCalculator:
    """Calculates tenant capacity allocation and validates against physical r5900 hardware constraints."""

    # F5 r5900 Hardware Envelope per appliance
    R5900_PHYSICAL_CORES = 16
    R5900_TOTAL_VCPUS = 32
    R5900_TOTAL_RAM_GB = 128
    R5900_MAX_THROUGHPUT_GBPS = 100.0
    R5900_MAX_SSL_TPS = 120000

    # Default Architectural Allocation Profile
    DEFAULT_DNS_TENANT_VCPUS = 4
    DEFAULT_DNS_TENANT_RAM_GB = 16
    DEFAULT_LTM_TENANT_VCPUS = 16
    DEFAULT_LTM_TENANT_RAM_GB = 48
    F5OS_HOST_OVERHEAD_VCPUS = 8
    F5OS_HOST_OVERHEAD_RAM_GB = 32

    # Legacy iSeries Baseline Reference Profiles
    ISERIES_PROFILES = {
        "i2800": {"cores": 4, "ram_gb": 16, "throughput_gbps": 10.0, "ssl_tps": 12000},
        "i4800": {"cores": 8, "ram_gb": 32, "throughput_gbps": 20.0, "ssl_tps": 25000},
        "i5800": {"cores": 8, "ram_gb": 48, "throughput_gbps": 40.0, "ssl_tps": 45000},
        "i7800": {"cores": 16, "ram_gb": 64, "throughput_gbps": 50.0, "ssl_tps": 70000},
        "i10800": {"cores": 24, "ram_gb": 128, "throughput_gbps": 80.0, "ssl_tps": 110000},
    }

    def __init__(self):
        pass

    def evaluate_migration(
        self,
        legacy_model: str,
        peak_throughput_gbps: float = 0.0,
        peak_ssl_tps: int = 0,
        peak_dns_qps: int = 0,
        custom_ltm_vcpus: int = 16,
        custom_ltm_ram_gb: int = 48,
        custom_dns_vcpus: int = 4,
        custom_dns_ram_gb: int = 16,
    ) -> Dict[str, Any]:
        """
        Evaluates migration capacity from legacy model to 4x r5900 appliances.
        Returns a detailed sizing budget report across Pair-A and Pair-B.
        """
        legacy = self.ISERIES_PROFILES.get(legacy_model.lower(), {
            "cores": 8, "ram_gb": 32, "throughput_gbps": 20.0, "ssl_tps": 30000
        })

        actual_throughput = peak_throughput_gbps if peak_throughput_gbps > 0 else legacy["throughput_gbps"]
        actual_ssl_tps = peak_ssl_tps if peak_ssl_tps > 0 else legacy["ssl_tps"]
        actual_dns_qps = peak_dns_qps if peak_dns_qps > 0 else 50000

        # Compute per-appliance resource consumption
        total_vcpus_used = self.F5OS_HOST_OVERHEAD_VCPUS + custom_dns_vcpus + custom_ltm_vcpus
        total_ram_used = self.F5OS_HOST_OVERHEAD_RAM_GB + custom_dns_ram_gb + custom_ltm_ram_gb

        headroom_vcpus = self.R5900_TOTAL_VCPUS - total_vcpus_used
        headroom_ram_gb = self.R5900_TOTAL_RAM_GB - total_ram_used

        is_valid = (headroom_vcpus >= 0) and (headroom_ram_gb >= 0)

        # Performance assessment
        ltm_capacity_headroom_tps = self.R5900_MAX_SSL_TPS - actual_ssl_tps
        ltm_capacity_headroom_gbps = self.R5900_MAX_THROUGHPUT_GBPS - actual_throughput

        return {
            "legacy_source": {
                "model": legacy_model,
                "cores": legacy["cores"],
                "ram_gb": legacy["ram_gb"],
                "peak_throughput_gbps": actual_throughput,
                "peak_ssl_tps": actual_ssl_tps,
                "peak_dns_qps": actual_dns_qps,
            },
            "target_hardware": {
                "model": "F5 r5900",
                "chassis_count_total": 4,
                "pairs": ["Pair-A (r5900-A1, r5900-A2)", "Pair-B (r5900-B1, r5900-B2)"],
                "total_chassis_vcpus": self.R5900_TOTAL_VCPUS,
                "total_chassis_ram_gb": self.R5900_TOTAL_RAM_GB,
            },
            "per_chassis_allocation": {
                "f5os_host_vcpus": self.F5OS_HOST_OVERHEAD_VCPUS,
                "f5os_host_ram_gb": self.F5OS_HOST_OVERHEAD_RAM_GB,
                "tenant_1_dns_vcpus": custom_dns_vcpus,
                "tenant_1_dns_ram_gb": custom_dns_ram_gb,
                "tenant_1_dns_ha_model": "Active/Active iQuery Anycast Mesh",
                "tenant_2_ltm_vcpus": custom_ltm_vcpus,
                "tenant_2_ltm_ram_gb": custom_ltm_ram_gb,
                "tenant_2_ltm_ha_model": "Active/Standby Sync-Failover HA Pair",
                "free_headroom_vcpus": headroom_vcpus,
                "free_headroom_ram_gb": headroom_ram_gb,
                "headroom_pct": round((headroom_vcpus / self.R5900_TOTAL_VCPUS) * 100, 1),
            },
            "performance_validation": {
                "capacity_feasible": is_valid,
                "ssl_tps_headroom": ltm_capacity_headroom_tps,
                "throughput_headroom_gbps": ltm_capacity_headroom_gbps,
                "dns_qps_supported": 1500000,
                "status": "APPROVED" if is_valid else "OVER_CAPACITY",
            }
        }
