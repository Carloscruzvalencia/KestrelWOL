"""
Tests unitarios para WolService (Servicio de Wake-on-LAN y seguridad de red).
"""

import unittest
from unittest.mock import MagicMock, patch
from services.wol_service import WolService


class TestWolService(unittest.TestCase):
    def setUp(self):
        self.mock_audit = MagicMock()
        self.wol = WolService(audit_service=self.mock_audit)

    # ---------------------------------------------------------
    # Validación y Sanitización de IP
    # ---------------------------------------------------------
    def test_validate_ip_valid(self):
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.254.1",
            "127.0.0.1",
            "255.255.255.255",
            "0.0.0.0",
        ]
        for ip in valid_ips:
            with self.subTest(ip=ip):
                self.assertTrue(self.wol.validate_ip(ip))

    def test_validate_ip_invalid(self):
        invalid_ips = [
            "256.1.1.1",
            "192.168.1",
            "192.168.1.1.1",
            "abc.def.ghi.jkl",
            "192.168.-1.1",
            "192.168.1.999",
            "",
            None,
        ]
        for ip in invalid_ips:
            with self.subTest(ip=ip):
                self.assertFalse(self.wol.validate_ip(ip))

    # ---------------------------------------------------------
    # Validación y Sanitización de MAC
    # ---------------------------------------------------------
    def test_validate_mac_valid(self):
        valid_macs = [
            "00:11:22:33:44:55",
            "00-11-22-33-44-55",
            "aa:bb:cc:dd:ee:ff",
            "AA:BB:CC:DD:EE:FF",
            "001122334455",
            "AABBCCDDEEFF",
        ]
        for mac in valid_macs:
            with self.subTest(mac=mac):
                self.assertTrue(self.wol.validate_mac(mac))

    def test_validate_mac_invalid(self):
        invalid_macs = [
            "00:11:22:33:44",
            "00:11:22:33:44:55:66",
            "00:11:22:33:44:GG",
            "INVALID_MAC_ADDR",
            "",
            None,
        ]
        for mac in invalid_macs:
            with self.subTest(mac=mac):
                self.assertFalse(self.wol.validate_mac(mac))

    # ---------------------------------------------------------
    # Construcción canónica del Magic Packet (102 bytes)
    # ---------------------------------------------------------
    def test_create_magic_packet_structure(self):
        mac = "00:11:22:33:44:55"
        packet = self.wol.create_magic_packet(mac)

        # Longitud total estricta: 6 bytes de 0xFF + 16 repeticiones de 6 bytes MAC = 102 bytes
        self.assertEqual(len(packet), 102)

        # Primeros 6 bytes deben ser 0xFF
        self.assertEqual(packet[:6], b"\xff" * 6)

        # Los siguientes 96 bytes deben ser 16 repeticiones del MAC
        mac_raw = bytes.fromhex("001122334455")
        self.assertEqual(packet[6:], mac_raw * 16)

    def test_create_magic_packet_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.wol.create_magic_packet("invalid-mac")

    # ---------------------------------------------------------
    # Envío y Sanitización en send_packet
    # ---------------------------------------------------------
    def test_send_packet_rejects_invalid_mac(self):
        success, msg = self.wol.send_packet("invalid-mac")
        self.assertFalse(success)
        self.assertIn("MAC", msg)
        self.mock_audit.log.assert_called_once()

    def test_send_packet_rejects_invalid_ip(self):
        success, msg = self.wol.send_packet("00:11:22:33:44:55", ip="999.999.999.999")
        self.assertFalse(success)
        self.assertIn("IP", msg)
        self.mock_audit.log.assert_called_once()

    @patch("socket.socket")
    def test_send_packet_success_with_socket(self, mock_socket_cls):
        mock_sock_instance = MagicMock()
        mock_socket_cls.return_value = mock_sock_instance

        success, msg = self.wol.send_packet("00:11:22:33:44:55", ip="192.168.1.50")
        self.assertTrue(success)
        self.assertTrue(mock_sock_instance.sendto.called)


if __name__ == "__main__":
    unittest.main()
