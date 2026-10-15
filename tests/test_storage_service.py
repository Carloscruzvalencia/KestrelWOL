"""
Tests unitarios para StorageService (Persistencia, Normalización y Sanitización CSV).
"""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from services.storage_service import StorageService


class TestStorageService(unittest.TestCase):
    def setUp(self):
        self.storage = StorageService()

    # ---------------------------------------------------------
    # Mitigación de CSV Formula Injection (CWE-1236)
    # ---------------------------------------------------------
    def test_sanitize_csv_cell_dangerous_characters(self):
        dangerous_inputs = [
            "=SUM(A1:A10)",
            "+cmd|' /C calc'!A0",
            "-2+3*4",
            "@import(something)",
            "\tTAB_INJECTION",
            "\rCARRIAGE_RETURN",
        ]
        for val in dangerous_inputs:
            with self.subTest(val=val):
                sanitized = self.storage._sanitize_csv_cell(val)
                self.assertTrue(sanitized.startswith("'"))
                self.assertEqual(sanitized[1:], val)

    def test_sanitize_csv_cell_safe_characters(self):
        safe_inputs = [
            "Servidor-01",
            "192.0.2.100",
            "00:00:5E:00:53:01",
            "Oficina Principal",
            "Normal text",
        ]
        for val in safe_inputs:
            with self.subTest(val=val):
                sanitized = self.storage._sanitize_csv_cell(val)
                self.assertEqual(sanitized, val)

    def test_desanitize_csv_cell(self):
        self.assertEqual(self.storage._desanitize_csv_cell("'=SUM(A1:A10)"), "=SUM(A1:A10)")
        self.assertEqual(self.storage._desanitize_csv_cell("Normal text"), "Normal text")
        self.assertEqual(self.storage._desanitize_csv_cell("'Regular text with quote"), "'Regular text with quote")

    # ---------------------------------------------------------
    # Normalización Canónica de Zonas
    # ---------------------------------------------------------
    def test_canonicalize_zone_defaults(self):
        self.assertEqual(self.storage.canonicalize_zone(""), "General")
        self.assertEqual(self.storage.canonicalize_zone(None), "General")
        self.assertEqual(self.storage.canonicalize_zone("   "), "General")

    def test_canonicalize_zone_existing_match(self):
        existing_machines = [
            {"name": "M1", "zone": "Servidores"},
            {"name": "M2", "zone": "Taller B"},
        ]
        # Búsqueda case-insensitive debe adoptar la grafía existente
        self.assertEqual(
            self.storage.canonicalize_zone("servidores", machines=existing_machines),
            "Servidores"
        )
        self.assertEqual(
            self.storage.canonicalize_zone("taller b", machines=existing_machines),
            "Taller B"
        )

    def test_canonicalize_zone_formatting_rules(self):
        # Letra única a mayúscula
        self.assertEqual(self.storage.canonicalize_zone("a", machines=[]), "A")
        # Prefijo 'zona x'
        self.assertEqual(self.storage.canonicalize_zone("zona a", machines=[]), "Zona A")
        self.assertEqual(self.storage.canonicalize_zone("zona servidores", machines=[]), "Zona Servidores")
        # Capitalización estándar
        self.assertEqual(self.storage.canonicalize_zone("desarrollo", machines=[]), "Desarrollo")

    # ---------------------------------------------------------
    # Exportación e Importación CSV en entorno temporal
    # ---------------------------------------------------------
    def test_csv_export_and_import_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "test_inventory.csv"
            machines_data = [
                {
                    "name": "PC-Admin",
                    "ip": "192.0.2.50",
                    "mac": "00:00:5E:00:53:01",
                    "zone": "Sistemas",
                    "schedule": {"enabled": True, "time": "08:00", "days": [0, 1, 2, 3, 4]}
                },
                {
                    "name": "PC-Taller",
                    "ip": "192.0.2.51",
                    "mac": "00:00:5E:00:53:02",
                    "zone": "Taller",
                    "schedule": {"enabled": False, "time": "09:00", "days": []}
                }
            ]

            # 1. Mockear load_machines para devolver machines_data y exportar
            with patch.object(self.storage, "load_machines", return_value=machines_data):
                success, msg = self.storage.export_machines_to_csv(csv_path)
                self.assertTrue(success)
                self.assertTrue(csv_path.exists())

            # 2. Mockear load_machines como vacío para importar de cero
            with patch.object(self.storage, "load_machines", return_value=[]):
                with patch.object(self.storage, "save_machines") as mock_save:
                    added, updated, msg = self.storage.import_machines_from_csv(csv_path)
                    self.assertEqual(added, 2)
                    self.assertEqual(updated, 0)
                    self.assertTrue(mock_save.called)
                    saved_machines = mock_save.call_args[0][0]
                    self.assertEqual(saved_machines[0]["name"], "PC-Admin")
                    self.assertEqual(saved_machines[0]["ip"], "192.0.2.50")
                    self.assertEqual(saved_machines[0]["mac"], "00:00:5e:00:53:01")
                    self.assertEqual(saved_machines[0]["zone"], "Sistemas")
                    self.assertTrue(saved_machines[0]["schedule"]["enabled"])
                    self.assertEqual(saved_machines[0]["schedule"]["days"], [0, 1, 2, 3, 4])


if __name__ == "__main__":
    unittest.main()
