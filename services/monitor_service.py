"""
Servicio de Monitorización de Estado de Equipos (services/monitor_service.py)
KestrelWOL - Arquitectura Offline-First
"""

import threading
import time
from typing import Any, Callable, Dict, List, Optional

from core.config import MONITOR_INTERVAL_SECONDS, MONITOR_ITEM_SLEEP_SECONDS
from services.system_service import SystemService


class MonitorService:
    """
    Worker en segundo plano para monitorización no invasiva de conectividad de equipos.
    Aplica pausas progresivas para mantener un consumo de CPU del 0% sin activar ventiladores.
    Totalmente desacoplado de la interfaz gráfica.
    """

    def __init__(
        self,
        on_status_change: Optional[Callable[[Dict[str, Any], str], None]] = None
    ):
        self._on_status_change = on_status_change
        self._machines: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None

    def set_machines(self, machines: List[Dict[str, Any]]) -> None:
        """Actualiza la lista de máquinas a monitorizar de forma thread-safe."""
        with self._lock:
            self._machines = list(machines)

    def set_callback(self, callback: Callable[[Dict[str, Any], str], None]) -> None:
        """Asigna o actualiza el callback que recibirá las actualizaciones de estado."""
        self._on_status_change = callback

    def start(self) -> None:
        """Inicia el ciclo de monitorización en un hilo secundario daemon."""
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return

        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._loop, daemon=True)
        self._worker_thread.start()

    def stop(self) -> None:
        """Detiene de forma limpia el bucle de monitorización."""
        self._stop_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
            self._worker_thread = None

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                current_targets = list(self._machines)

            for machine in current_targets:
                if self._stop_event.is_set():
                    break

                ip = machine.get("ip")
                mac = machine.get("mac")
                status = SystemService.check_machine_status(ip, mac)

                if self._on_status_change:
                    self._on_status_change(machine, status)

                # Pausa suave de 300 ms entre cada puesto para evitar picos de CPU
                time.sleep(MONITOR_ITEM_SLEEP_SECONDS)

            # Espera no bloqueante entre ciclos completos respetando la parada inmediata
            self._stop_event.wait(timeout=MONITOR_INTERVAL_SECONDS)
