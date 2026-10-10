"""
Unit Tests for F5 Assessment Engine components:
- TMOSConfParser
- DeprecationAnalyzer
- R5900SizingCalculator
- AS3Converter
- GTMConverter
"""

import unittest
from pathlib import Path

from tools.assessment.conf_parser import TMOSConfParser
from tools.assessment.deprecation_analyzer import DeprecationAnalyzer
from tools.assessment.sizing_calculator import R5900SizingCalculator
from tools.assessment.as3_converter import AS3Converter
from tools.assessment.gtm_converter import GTMConverter


class TestAssessmentEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.fixture_path = Path("tests/fixtures/legacy_iseries_bigip.conf")
        cls.parser = TMOSConfParser()
        cls.catalog = cls.parser.parse_file(str(cls.fixture_path))

    def test_parser_extracts_virtuals(self):
        virtuals = self.catalog.get("virtual_servers", {})
        self.assertIn("vs_ecommerce_https", virtuals)
        self.assertIn("vs_api_gateway_https", virtuals)
        self.assertEqual(virtuals["vs_ecommerce_https"]["ip"], "10.1.100.50")
        self.assertEqual(virtuals["vs_ecommerce_https"]["port"], "443")

    def test_parser_extracts_pools_and_members(self):
        pools = self.catalog.get("pools", {})
        self.assertIn("pool_web_frontend", pools)
        members = pools["pool_web_frontend"]["members"]
        self.assertEqual(len(members), 2)
        member_ips = [m["ip"] for m in members]
        self.assertIn("192.168.10.11", member_ips)
        self.assertIn("192.168.10.12", member_ips)

    def test_deprecation_analyzer_detects_compat_and_rc4(self):
        analyzer = DeprecationAnalyzer()
        findings = analyzer.analyze(self.catalog)
        severities = [f.severity for f in findings]
        categories = [f.category for f in findings]

        self.assertIn("CRITICAL", severities)
        self.assertIn("HIGH", severities)
        self.assertIn("HARDWARE_CRYPTO", categories)
        self.assertIn("SSL_CIPHERS", categories)
        self.assertIn("NETWORKING", categories)

    def test_r5900_sizing_calculator(self):
        sizer = R5900SizingCalculator()
        result = sizer.evaluate_migration("i5800")
        self.assertEqual(result["performance_validation"]["status"], "APPROVED")
        self.assertEqual(result["per_chassis_allocation"]["tenant_1_dns_vcpus"], 4)
        self.assertEqual(result["per_chassis_allocation"]["tenant_2_ltm_vcpus"], 16)
        self.assertEqual(result["per_chassis_allocation"]["free_headroom_vcpus"], 4)

    def test_as3_converter_generates_valid_declaration(self):
        converter = AS3Converter(tenant_name="Tenant_LTM_Test")
        payload = converter.convert(self.catalog)

        self.assertEqual(payload["class"], "AS3")
        declaration = payload["declaration"]
        self.assertIn("Tenant_LTM_Test", declaration)
        tenant = declaration["Tenant_LTM_Test"]
        self.assertIn("vs_ecommerce_https", tenant)
        app = tenant["vs_ecommerce_https"]
        self.assertIn("service_vs_ecommerce_https", app)
        self.assertEqual(app["service_vs_ecommerce_https"]["class"], "Service_HTTPS")
        self.assertEqual(app["service_vs_ecommerce_https"]["virtualAddresses"], ["10.1.100.50"])

    def test_gtm_converter_generates_gslb_wideips(self):
        converter = GTMConverter()
        payload = converter.convert(self.catalog)

        self.assertEqual(payload["legacy_wideip_count"], 1)
        wideips = payload["wideips"]
        self.assertEqual(wideips[0]["fqdn"], "portal.enterprise.com")
        self.assertEqual(len(payload["iquery_servers"]), 2)


if __name__ == "__main__":
    unittest.main()
