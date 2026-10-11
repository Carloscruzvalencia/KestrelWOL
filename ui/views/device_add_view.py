"""
Vista de Formulario para Agregar Dispositivos (ui/views/device_add_view.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_BLUE,
    BG_CARD,
    BG_INPUT,
    FONTS,
    HOVER_BLUE,
    HOVER_SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
)
from ui.components.zone_dropdown_input import ZoneDropdownInput


class DeviceAddView(ctk.CTkFrame):
    """
    Panel superior con formulario para dar de alta nuevos puestos en la red:
    - Campos: Nombre, IP, MAC y Zona con desplegable de zonas existentes.
    - Botones de Escanear Red y Guardar en Panel.
    - Notifica al orquestador a través de callbacks sin lógica de almacenamiento acoplada.
    """

    def __init__(
        self,
        parent,
        get_zones_callback: Optional[Callable[[], List[str]]] = None,
        on_add_device: Optional[Callable[[Dict[str, str]], None]] = None,
        on_open_scanner: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=BG_CARD,
            corner_radius=8,
            **kwargs
        )
        self.get_zones_callback = get_zones_callback
        self.on_add_device = on_add_device
        self.on_open_scanner = on_open_scanner

        self._build_ui()

    def _build_ui(self) -> None:
        lbl_sec = ctk.CTkLabel(
            self,
            text="Agregar Nuevo Dispositivo",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        lbl_sec.pack(anchor="w", padx=16, pady=(12, 6))

        inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        inputs_frame.pack(fill=tk.X, padx=16, pady=(0, 8))

        # 1. Nombre
        ctk.CTkLabel(inputs_frame, text="Nombre:", font=FONTS["body_bold"], text_color=TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.entry_name = ctk.CTkEntry(inputs_frame, font=FONTS["body_normal"], height=30, fg_color=BG_CARD, border_color=BG_INPUT, border_width=1)
        self.entry_name.grid(row=0, column=1, padx=(0, 10), sticky="ew")

        # 2. IP
        ctk.CTkLabel(inputs_frame, text="IP:", font=FONTS["body_bold"], text_color=TEXT_MUTED).grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.entry_ip = ctk.CTkEntry(inputs_frame, font=FONTS["body_normal"], height=30, fg_color=BG_CARD, border_color=BG_INPUT, border_width=1)
        self.entry_ip.grid(row=0, column=3, padx=(0, 10), sticky="ew")

        # 3. MAC
        ctk.CTkLabel(inputs_frame, text="MAC:", font=FONTS["body_bold"], text_color=TEXT_MUTED).grid(row=0, column=4, sticky="w", padx=(0, 4))
        self.entry_mac = ctk.CTkEntry(inputs_frame, font=FONTS["body_normal"], height=30, fg_color=BG_CARD, border_color=BG_INPUT, border_width=1)
        self.entry_mac.grid(row=0, column=5, padx=(0, 10), sticky="ew")

        # 4. Zona con selector desplegable
        ctk.CTkLabel(inputs_frame, text="Zona:", font=FONTS["body_bold"], text_color=TEXT_MUTED).grid(row=0, column=6, sticky="w", padx=(0, 4))
        self.entry_zone = ZoneDropdownInput(inputs_frame, get_zones_callback=self.get_zones_callback, height=30)
        self.entry_zone.set("Zona A")
        self.entry_zone.grid(row=0, column=7, sticky="ew")

        inputs_frame.columnconfigure(1, weight=2)
        inputs_frame.columnconfigure(3, weight=2)
        inputs_frame.columnconfigure(5, weight=2)
        inputs_frame.columnconfigure(7, weight=2)

        # Botonera inferior del formulario
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        ctk.CTkButton(
            actions_frame,
            text="🔍 Escanear Red local",
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=28,
            command=lambda: self.on_open_scanner() if self.on_open_scanner else None
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            actions_frame,
            text="💾 Guardar en Panel",
            font=FONTS["body_bold"],
            fg_color=ACCENT_BLUE,
            hover_color=HOVER_BLUE,
            text_color=TEXT_PRIMARY,
            height=28,
            command=self._on_submit
        ).pack(side=tk.RIGHT)

    def _on_submit(self) -> None:
        data = {
            "name": self.entry_name.get().strip(),
            "ip": self.entry_ip.get().strip(),
            "mac": self.entry_mac.get().strip(),
            "zone": self.entry_zone.get().strip() or "General"
        }
        if self.on_add_device:
            self.on_add_device(data)

    def populate_from_scan(self, ip: str, mac: str, host: str) -> None:
        """Rellena los campos con los datos obtenidos desde el escáner."""
        self.entry_name.delete(0, tk.END)
        if host and host != "Unknown" and host != "Dispositivo de red":
            self.entry_name.insert(0, host)

        self.entry_ip.delete(0, tk.END)
        self.entry_ip.insert(0, ip)

        self.entry_mac.delete(0, tk.END)
        self.entry_mac.insert(0, mac)

    def clear(self, keep_zone: Optional[str] = None) -> None:
        """Limpia los campos del formulario."""
        self.entry_name.delete(0, tk.END)
        self.entry_ip.delete(0, tk.END)
        self.entry_mac.delete(0, tk.END)
        if keep_zone:
            self.entry_zone.set(keep_zone)
