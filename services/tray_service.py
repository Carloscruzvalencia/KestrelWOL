"""
Servicio de Icono en Bandeja del Sistema (services/tray_service.py)
KestrelWOL - Arquitectura Desacoplada Offline-First
"""

import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray


class TrayService:
    """
    Gestiona el icono en la bandeja del sistema (System Tray):
    - Permite minimizar la aplicación sin detener los servicios programados (Scheduler).
    - Desacoplado de la GUI: no utiliza Tkinter ni referencias a widgets.
    """

    def __init__(
        self,
        on_restore: Optional[Callable[[], None]] = None,
        on_quit: Optional[Callable[[], None]] = None,
        app_title: str = "WakeOnLan Controller"
    ):
        self._on_restore = on_restore
        self._on_quit = on_quit
        self._app_title = app_title
        self._icon: Optional[pystray.Icon] = None
        self._lock = threading.Lock()

    def _generate_icon_image(self) -> Image.Image:
        """Genera un icono circular nítido en memoria sin dependencias externas."""
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        dc = ImageDraw.Draw(img)
        # Círculo base oscuro
        dc.ellipse((4, 4, 60, 60), fill="#0f172a", outline="#334155", width=2)
        # Indicador esmeralda central (señal de actividad)
        dc.ellipse((20, 20, 44, 44), fill="#10b981")
        return img

    def start(self) -> None:
        """Inicia el icono en la bandeja del sistema en un hilo secundario."""
        with self._lock:
            if self._icon is not None:
                return

            image = self._generate_icon_image()
            menu = pystray.Menu(
                pystray.MenuItem("Abrir Panel", self._handle_restore, default=True),
                pystray.MenuItem("Cerrar Aplicación", self._handle_quit)
            )

            self._icon = pystray.Icon(
                "wakeonlan_app",
                image,
                self._app_title,
                menu=menu
            )

            threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self) -> None:
        """Detiene y retira el icono de la bandeja."""
        with self._lock:
            if self._icon is not None:
                try:
                    self._icon.stop()
                except Exception:
                    pass
                self._icon = None

    def _handle_restore(self, icon=None, item=None) -> None:
        if self._on_restore:
            self._on_restore()

    def _handle_quit(self, icon=None, item=None) -> None:
        self.stop()
        if self._on_quit:
            self._on_quit()
