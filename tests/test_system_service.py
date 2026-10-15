"""
Tests unitarios para SystemService (Utilidades de Sistema, ARP e Instancia Única).
"""

import unittest
from unittest.mock import MagicMock, patch

from services.system_service import IPV4_SAFE_REGEX, SystemService


class TestSystemService(unittest.TestCase):
    def test_ipv4_safe_regex(self):
        self.assertTrue(IPV4_SAFE_REGEX.match("192.0.2.1"))
        self.assertTrue(IPV4_SAFE_REGEX.match("10.0.0.254"))
        self.assertFalse(IPV4_SAFE_REGEX.match("192.0.2.300"))
        self.assertFalse(IPV4_SAFE_REGEX.match("malicious;rm -rf /"))

    @patch.object(SystemService, "get_arp_table")
    def test_get_arp_devices_filters_broadcast_and_ignored(self, mock_get_arp_table):
        # Simular tabla ARP del sistema
        mock_get_arp_table.return_value = {
            "192.0.2.1": "00:00:5E:00:53:01",
            "192.0.2.50": "00:00:5E:00:53:02",
            "192.0.2.255": "ff:ff:ff:ff:ff:ff",  # Broadcast -> debe filtrarse
            "224.0.0.22": "01:00:5e:00:00:16",   # Multicast -> debe filtrarse
            "192.0.2.99": "00:00:5E:00:53:99",   # Ignorada -> debe filtrarse
        }

        devices = SystemService.get_arp_devices(ignored_ips=["192.0.2.99"])
        ips_found = [d["ip"] for d in devices]

        self.assertIn("192.0.2.1", ips_found)
        self.assertIn("192.0.2.50", ips_found)
        self.assertNotIn("192.0.2.255", ips_found)
        self.assertNotIn("224.0.0.22", ips_found)
        self.assertNotIn("192.0.2.99", ips_found)


if __name__ == "__main__":
    unittest.main()
