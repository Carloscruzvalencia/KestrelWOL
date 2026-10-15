"""
Contrato de Comunicación y Despacho Seguro de Eventos (core/events.py)
KestrelWOL - Arquitectura Offline-First

Garantiza la sincronización thread-safe entre workers secundarios y el Main Thread
de la GUI mediante el uso estricto de root.after(0, ...), colas concurrentes y tipado fuerte.
"""

from dataclasses import dataclass
from enum import Enum, auto
import queue
from typing import Any, Callable, Optional


class EventType(Enum):
    """Tipos de eventos que los workers pueden emitir hacia el orquestador UI."""
    STATUS_UPDATED = auto()       # Cambio de estado de un equipo (online/offline/error)
    WAKE_PROGRESS = auto()        # Progreso de encendido escalonado (actual/total)
    WAKE_FINISHED = auto()        # Finalización de encendido masivo o individual
    SCAN_DEVICE_FOUND = auto()    # Dispositivo detectado durante el escaneo ARP
    SCAN_FINISHED = auto()        # Finalización del escaneo de red
    SCHEDULE_TRIGGERED = auto()   # Alarma de encendido programado activada
    ERROR_OCCURRED = auto()       # Error capturado en subproceso o worker


@dataclass(frozen=True)
class AppEvent:
    """Dataclass inmutable que encapsula un evento emitido por un worker."""
    event_type: EventType
    payload: Any = None
    message: str = ""


def safe_gui_dispatch(root: Any, callback: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """
    Wrapper de despacho seguro hacia el bucle principal de eventos de la GUI.
    
    Asegura que cualquier callback disparado desde un hilo de trabajo secundario
    (I/O, ping, sockets, subprocess) se ejecute SIEMPRE en el Main Thread mediante
    `root.after(0, ...)`, evitando inconsistencias de memoria o bloqueos de renderizado.
    
    Args:
        root: Instancia principal de la ventana (ctk.CTk o tk.Tk) con soporte de after().
        callback: Función de la interfaz que actualizará los widgets.
        *args, **kwargs: Parámetros a pasar al callback.
    """
    if root is None or not hasattr(root, "after"):
        # Modo headless o pruebas unitarias
        callback(*args, **kwargs)
        return

    try:
        # Programar la llamada en el siguiente ciclo de la cola de eventos de Tk
        root.after(0, lambda: callback(*args, **kwargs))
    except Exception:
        # En caso de que la ventana esté en proceso de destrucción (cierre de app)
        pass


class ThreadSafeEventQueue:
    """
    Cola de mensajes concurrente que permite a los workers encolar eventos de forma
    desacoplada para ser consumidos periódicamente por la interfaz gráfica.
    """

    def __init__(self, maxsize: int = 1000):
        self._queue: queue.Queue[AppEvent] = queue.Queue(maxsize=maxsize)

    def post(self, event_type: EventType, payload: Any = None, message: str = "") -> None:
        """Encola un evento desde cualquier hilo secundario sin bloquear."""
        try:
            self._queue.put_nowait(AppEvent(event_type=event_type, payload=payload, message=message))
        except queue.Full:
            pass

    def drain(self) -> list[AppEvent]:
        """Extrae todos los eventos acumulados hasta el momento (no bloqueante)."""
        events: list[AppEvent] = []
        while not self._queue.empty():
            try:
                events.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return events
