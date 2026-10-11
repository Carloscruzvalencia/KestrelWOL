"""
Vista de Cuadrícula Responsiva de Dispositivos (ui/views/device_grid_view.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    BG_DARK,
    BREAKPOINT_THREE_COLUMNS,
    FONTS,
    TEXT_MUTED,
)
from ui.components.device_card import DeviceCardComponent


class DeviceGridView(ctk.CTkScrollableFrame):
    """
    Contenedor con scroll vertical que organiza las tarjetas de equipos en una
    cuadrícula responsiva (2 o 3 columnas según el ancho disponible).
    """

    def __init__(
        self,
        parent,
        on_wake_device: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_edit_device: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_delete_device: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_schedule_device: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_remote_control_device: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_launch_rdp: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_launch_ssh: Optional[Callable[[Dict[str, Any]], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=BG_DARK,
            corner_radius=0,
            **kwargs
        )
        self.on_wake_device = on_wake_device
        self.on_edit_device = on_edit_device
        self.on_delete_device = on_delete_device
        self.on_schedule_device = on_schedule_device
        self.on_remote_control_device = on_remote_control_device
        self.on_launch_rdp = on_launch_rdp
        self.on_launch_ssh = on_launch_ssh

        self._cards: List[DeviceCardComponent] = []
        self._current_cols = 2
        self._last_devices: List[Dict[str, Any]] = []
        self._show_network_info = False

        self.bind("<Configure>", self._on_configure)

    def render_devices(self, devices: List[Dict[str, Any]]) -> None:
        """Limpia y reconstruye la cuadrícula con los dispositivos recibidos."""
        self._last_devices = list(devices)

        # Destruir únicamente las tarjetas previas y el mensaje de vacío
        for card in self._cards:
            try:
                card.destroy()
            except Exception:
                pass
        self._cards.clear()

        if hasattr(self, "_empty_frame") and self._empty_frame:
            try:
                self._empty_frame.destroy()
            except Exception:
                pass
            self._empty_frame = None

        if not devices:
            self._empty_frame = ctk.CTkFrame(self, fg_color="transparent")
            self._empty_frame.grid(row=0, column=0, columnspan=self._current_cols, sticky="nsew", pady=40)
            ctk.CTkLabel(
                self._empty_frame,
                text="No hay dispositivos registrados en esta selección.",
                font=FONTS["title_section"],
                text_color=TEXT_MUTED
            ).pack()
            return

        for c in range(self._current_cols):
            self.columnconfigure(c, weight=1)

        for idx, machine in enumerate(devices):
            row = idx // self._current_cols
            col = idx % self._current_cols

            card = DeviceCardComponent(
                self,
                machine=machine,
                on_wake=self.on_wake_device,
                on_edit=self.on_edit_device,
                on_delete=self.on_delete_device,
                on_schedule=self.on_schedule_device,
                on_remote_control=self.on_remote_control_device,
                on_launch_rdp=self.on_launch_rdp,
                on_launch_ssh=self.on_launch_ssh,
                show_network_info=self._show_network_info
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self._cards.append(card)

    def toggle_all_network_visibility(self) -> bool:
        """Alterna la visibilidad de la IP y MAC en todas las tarjetas de la cuadrícula."""
        self._show_network_info = not self._show_network_info
        for card in self._cards:
            card.set_network_visibility(self._show_network_info)
        return self._show_network_info

    def update_device_status(self, ip: Optional[str], mac: Optional[str], status: str) -> None:
        """Actualiza el estado gráfico de una tarjeta específica de forma thread-safe."""
        for card in self._cards:
            c_mac = card.machine.get("mac", "")
            c_ip = card.machine.get("ip", "")
            if (mac and c_mac.lower() == mac.lower()) or (ip and c_ip == ip):
                card.update_status(status)

    def _on_configure(self, event) -> None:
        new_cols = 3 if event.width >= BREAKPOINT_THREE_COLUMNS else 2
        if new_cols != self._current_cols:
            self._current_cols = new_cols
            if self._last_devices:
                self.render_devices(self._last_devices)
