"""
Vista de Formulario para Agregar Dispositivos (ui/views/device_add_view.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from typing import Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    BG_INPUT,
    FONTS,
    HOVER_SECONDARY,
    TEXT_DISABLED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from ui.components.icons import get_icon
from ui.components.zone_dropdown_input import ZoneDropdownInput


class DeviceAddView(ctk.CTkFrame):
    """
    Panel superior con formulario para dar de alta nuevos puestos en la red:
    - Campos: Nombre, IP, MAC y Zona con desplegable de zonas existentes.
    - Botones monocromos con bordes hairline 1px y tipografía monoespaciada en campos técnicos.
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
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS,
            **kwargs
        )
        self.get_zones_callback = get_zones_callback
        self.on_add_device = on_add_device
        self.on_open_scanner = on_open_scanner

        self._build_ui()

    def _build_ui(self) -> None:
        lbl_sec = ctk.CTkLabel(
            self,
            text="AGREGAR DISPOSITIVO",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED,
            anchor="w"
        )
        lbl_sec.pack(anchor="w", padx=16, pady=(10, 6))

        inputs_frame = ctk.CTkFrame(self, fg_color="transparent")
        inputs_frame.pack(fill=tk.X, padx=16, pady=(0, 10))

        entry_kwargs = {
            "height": 30,
            "fg_color": BG_INPUT,
            "border_color": BG_BORDER_BUTTON,
            "border_width": 1,
            "corner_radius": UI_RADIUS,
            "text_color": TEXT_PRIMARY,
        }

        # 1. Nombre
        ctk.CTkLabel(inputs_frame, text="Nombre", font=FONTS["caption_bold"], text_color=TEXT_DISABLED).grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.entry_name = ctk.CTkEntry(inputs_frame, font=FONTS["body_normal"], placeholder_text="WS-01", **entry_kwargs)
        self.entry_name.grid(row=0, column=1, padx=(0, 12), sticky="ew")

        # 2. IP
        ctk.CTkLabel(inputs_frame, text="IP", font=FONTS["caption_bold"], text_color=TEXT_DISABLED).grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.entry_ip = ctk.CTkEntry(inputs_frame, font=FONTS["mono_data"], placeholder_text="192.168.1.50", **entry_kwargs)
        self.entry_ip.grid(row=0, column=3, padx=(0, 12), sticky="ew")

        # 3. MAC
        ctk.CTkLabel(inputs_frame, text="MAC", font=FONTS["caption_bold"], text_color=TEXT_DISABLED).grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.entry_mac = ctk.CTkEntry(inputs_frame, font=FONTS["mono_data"], placeholder_text="AA:BB:CC:DD:EE:FF", **entry_kwargs)
        self.entry_mac.grid(row=0, column=5, padx=(0, 12), sticky="ew")

        # 4. Zona con selector desplegable
        ctk.CTkLabel(inputs_frame, text="Zona", font=FONTS["caption_bold"], text_color=TEXT_DISABLED).grid(row=0, column=6, sticky="w", padx=(0, 6))
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
            text="Escanear Red local",
            image=get_icon("search", TEXT_SECONDARY, 14),
            compound="left",
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            height=30,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_open_scanner() if self.on_open_scanner else None
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            actions_frame,
            text="Guardar en Panel",
            image=get_icon("plus", TEXT_PRIMARY, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_PRIMARY,
            height=30,
            corner_radius=UI_RADIUS,
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
