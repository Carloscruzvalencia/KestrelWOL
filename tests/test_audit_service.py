"""
Tests unitarios para AuditService (Auditoría Forense y Hash Chaining SHA-256).
"""

import hashlib
import unittest
from services.audit_service import AuditService


class TestAuditService(unittest.TestCase):
    def setUp(self):
        self.audit = AuditService()

    def test_singleton_instance(self):
        audit2 = AuditService()
        self.assertIs(self.audit, audit2)

    def test_hash_chaining_progression(self):
        initial_hash = self.audit._last_hash

        # Disparar un log
        self.audit.log(
            action="TEST_ACTION_1",
            target_name="Host-Alpha",
            ip="192.0.2.10",
            mac="00:00:5E:00:53:01",
            status="SUCCESS",
            details="Test verification"
        )
        hash_1 = self.audit._last_hash
        self.assertNotEqual(initial_hash, hash_1)

        # Disparar un segundo log
        self.audit.log(
            action="TEST_ACTION_2",
            target_name="Host-Beta",
            ip="192.0.2.20",
            mac="00:00:5E:00:53:02",
            status="SUCCESS",
            details="Second verification"
        )
        hash_2 = self.audit._last_hash
        self.assertNotEqual(hash_1, hash_2)

    def test_log_chain_cryptographic_verification(self):
        previous_hash = self.audit._last_hash
        action = "CRYPTO_VERIFY"
        target_name = "Host-Gamma"
        ip = "192.0.2.30"
        mac = "00:00:5E:00:53:03"
        status = "SUCCESS"
        details = "Testing exact sha256 output"

        user = self.audit._get_current_user()
        expected_msg = (
            f"[USER: {user}] "
            f"[ACTION: {action}] "
            f"[HOST: {target_name}] "
            f"[IP: {ip}] "
            f"[MAC: {mac}] "
            f"[STATUS: {status}] "
            f"[INFO: {details}]"
        )

        expected_payload = f"{previous_hash}|{expected_msg}".encode("utf-8")
        expected_hash = hashlib.sha256(expected_payload).hexdigest()[:16]

        self.audit.log(
            action=action,
            target_name=target_name,
            ip=ip,
            mac=mac,
            status=status,
            details=details
        )

        self.assertEqual(self.audit._last_hash, expected_hash)


if __name__ == "__main__":
    unittest.main()
