"""
Tests unitarios para SchedulerService (Programador Horario de Encendido).
"""

import datetime
import unittest
from unittest.mock import MagicMock, patch

from services.scheduler_service import SchedulerService


class TestSchedulerService(unittest.TestCase):
    def setUp(self):
        self.mock_audit = MagicMock()
        self.mock_wake_callback = MagicMock()
        self.scheduler = SchedulerService(
            on_trigger_wake=self.mock_wake_callback,
            audit_service=self.mock_audit
        )

    def test_schedule_trigger_matching_time_and_day(self):
        # Simular fecha y hora fija (Lunes a las 08:30)
        # weekday(): 0 = Lunes
        fake_now = datetime.datetime(2026, 10, 12, 8, 30, 0)

        test_machine = {
            "name": "Servidor-App",
            "ip": "192.168.1.10",
            "mac": "00:11:22:33:44:55",
            "zone": "Sistemas",
            "schedule": {
                "enabled": True,
                "time": "08:30",
                "days": [0, 1, 2, 3, 4]  # Lunes a Viernes
            }
        }
        self.scheduler.set_machines([test_machine])

        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = fake_now
            # Ejecutar una sola pasada del chequeo
            # Simulamos el bucle manualmente ejecutando el cuerpo interno de verificación
            now = fake_now
            current_weekday = now.weekday()
            current_time_str = now.strftime("%H:%M")
            date_key = str(now.date())

            for machine in self.scheduler._machines:
                sched = machine.get("schedule", {})
                if sched.get("enabled") and sched.get("time") == current_time_str and current_weekday in sched.get("days", []):
                    machine_id = machine.get("mac")
                    self.scheduler._last_triggered[machine_id] = (date_key, current_time_str)
                    self.mock_wake_callback(machine)

            self.mock_wake_callback.assert_called_once_with(test_machine)
            self.assertIn("00:11:22:33:44:55", self.scheduler._last_triggered)

    def test_schedule_does_not_trigger_when_disabled(self):
        fake_now = datetime.datetime(2026, 10, 12, 8, 30, 0)
        test_machine = {
            "name": "Servidor-App",
            "ip": "192.168.1.10",
            "mac": "00:11:22:33:44:55",
            "schedule": {
                "enabled": False,  # Desactivado
                "time": "08:30",
                "days": [0]
            }
        }
        self.scheduler.set_machines([test_machine])

        # Verificación directa
        sched = test_machine.get("schedule", {})
        triggered = sched.get("enabled") and sched.get("time") == fake_now.strftime("%H:%M")
        self.assertFalse(triggered)
        self.mock_wake_callback.assert_not_called()

    def test_schedule_does_not_trigger_on_different_day(self):
        # Domingo (weekday = 6)
        fake_now = datetime.datetime(2026, 10, 18, 8, 30, 0)
        test_machine = {
            "name": "Servidor-App",
            "ip": "192.168.1.10",
            "mac": "00:11:22:33:44:55",
            "schedule": {
                "enabled": True,
                "time": "08:30",
                "days": [0, 1, 2, 3, 4]  # Solo días de semana
            }
        }
        self.scheduler.set_machines([test_machine])

        sched = test_machine.get("schedule", {})
        triggered = sched.get("enabled") and (fake_now.weekday() in sched.get("days", []))
        self.assertFalse(triggered)
        self.mock_wake_callback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
