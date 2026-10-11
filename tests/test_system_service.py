"""
Tests unitarios para SystemService (Utilidades de Sistema, ARP e Instancia Única).
"""

import unittest
from unittest.mock import MagicMock, patch

from services.system_service import IPV4_SAFE_REGEX, SystemService


class TestSystemService(unittest.TestCase):
    def test_ipv4_safe_regex(self):
        self.assertTrue(IPV4_SAFE_REGEX.match("192.168.1.1"))
        self.assertTrue(IPV4_SAFE_REGEX.match("10.0.0.254"))
        self.assertFalse(IPV4_SAFE_REGEX.match("192.168.1.300"))
        self.assertFalse(IPV4_SAFE_REGEX.match("malicious;rm -rf /"))

    @patch.object(SystemService, "get_arp_table")
    def test_get_arp_devices_filters_broadcast_and_ignored(self, mock_get_arp_table):
        # Simular tabla ARP del sistema
        mock_get_arp_table.return_value = {
            "192.168.1.1": "00:11:22:33:44:01",
            "192.168.1.50": "00:11:22:33:44:02",
            "192.168.1.255": "ff:ff:ff:ff:ff:ff",  # Broadcast -> debe filtrarse
            "224.0.0.22": "01:00:5e:00:00:16",    # Multicast -> debe filtrarse
            "192.168.1.99": "00:11:22:33:44:99",  # Ignorada -> debe filtrarse
        }

        devices = SystemService.get_arp_devices(ignored_ips=["192.168.1.99"])
        ips_found = [d["ip"] for d in devices]

        self.assertIn("192.168.1.1", ips_found)
        self.assertIn("192.168.1.50", ips_found)
        self.assertNotIn("192.168.1.255", ips_found)
        self.assertNotIn("224.0.0.22", ips_found)
        self.assertNotIn("192.168.1.99", ips_found)


if __name__ == "__main__":
    unittest.main()
