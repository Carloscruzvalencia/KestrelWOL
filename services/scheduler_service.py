"""
Servicio de Programación Horaria de Encendido (services/scheduler_service.py)
KestrelWOL - Arquitectura Offline-First
"""

import datetime
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.config import SCHEDULE_CHECK_INTERVAL_SECONDS
from services.audit_service import AuditService


class SchedulerService:
    """
    Worker en segundo plano para encendidos programados en base a horarios semanales.
    Evita disparos repetidos en el mismo minuto.
    """

    def __init__(
        self,
        on_trigger_wake: Optional[Callable[[Dict[str, Any]], None]] = None,
        audit_service: Optional[AuditService] = None
    ):
        self._on_trigger_wake = on_trigger_wake
        self._audit = audit_service or AuditService()
        self._machines: List[Dict[str, Any]] = []
        self._last_triggered: Dict[str, Tuple[str, str]] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None

    def set_machines(self, machines: List[Dict[str, Any]]) -> None:
        """Actualiza la lista de máquinas para verificación de horarios."""
        with self._lock:
            self._machines = list(machines)

    def set_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Asigna el callback invocado cuando una alarma horaria debe emitir el paquete."""
        self._on_trigger_wake = callback

    def start(self) -> None:
        """Inicia el worker del programador en segundo plano."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return

        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._loop, daemon=True)
        self._worker_thread.start()

    def stop(self) -> None:
        """Detiene de forma limpia el hilo del programador."""
        self._stop_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
            self._worker_thread = None

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                now = datetime.datetime.now()
                current_weekday = now.weekday()
                current_time_str = now.strftime("%H:%M")
                date_key = str(now.date())

                with self._lock:
                    targets = list(self._machines)

                for machine in targets:
                    schedule = machine.get("schedule")
                    if not schedule or not schedule.get("enabled"):
                        continue

                    target_time = schedule.get("time", "")
                    days = schedule.get("days", [])

                    if target_time == current_time_str and current_weekday in days:
                        machine_id = machine.get("mac") or machine.get("name") or "unknown"

                        last_fired = self._last_triggered.get(machine_id)
                        if last_fired != (date_key, current_time_str):
                            self._last_triggered[machine_id] = (date_key, current_time_str)
                            self._audit.log(
                                "SCHEDULED_WAKE_TRIGGERED",
                                target_name=machine.get("name", "N/A"),
                                ip=machine.get("ip", "N/A"),
                                mac=machine.get("mac", "N/A"),
                                status="TRIGGERED",
                                details=f"Horario semanal alcanzado: {current_time_str}"
                            )
                            if self._on_trigger_wake:
                                self._on_trigger_wake(machine)

            except Exception as e:
                self._audit.log("SCHEDULE_WORKER_ERROR", status="ERROR", details=str(e))

            # Espera no bloqueante respetando la señal de parada inmediata
            self._stop_event.wait(timeout=SCHEDULE_CHECK_INTERVAL_SECONDS)
