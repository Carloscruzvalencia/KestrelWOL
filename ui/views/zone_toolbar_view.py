"""
Vista de Barra de Presets de Zonas (ui/views/zone_toolbar_view.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_BLUE,
    ACCENT_EMERALD,
    BG_INPUT,
    FONTS,
    HOVER_BLUE,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class ZoneToolbarView(ctk.CTkFrame):
    """
    Barra horizontal con selector de presets de zonas y botón rápido de encendido:
    - Botones dinámicos: [Todos (N)], [Zona A (M)], [Zona B (K)]...
    - Botón de encendido por zona contextual.
    - Notifica cambios de selección y órdenes de encendido al orquestador.
    """

    def __init__(
        self,
        parent,
        on_zone_selected: Optional[Callable[[str], None]] = None,
        on_wake_zone: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )
        self.on_zone_selected = on_zone_selected
        self.on_wake_zone = on_wake_zone

        self._active_zone = "Todos"
        self._zone_counts: Dict[str, int] = {"Todos": 0}

        self.left_box = ctk.CTkFrame(self, fg_color="transparent")
        self.left_box.pack(side=tk.LEFT, fill=tk.Y)

        self.right_box = ctk.CTkFrame(self, fg_color="transparent")
        self.right_box.pack(side=tk.RIGHT, fill=tk.Y)

        self.render_zones(["Todos"], {"Todos": 0}, "Todos")

    def render_zones(
        self,
        zones_list: List[str],
        zone_counts: Dict[str, int],
        selected_zone: str
    ) -> None:
        """Reconstruye los botones de zonas según la lista canónica calculada."""
        self._active_zone = selected_zone
        self._zone_counts = zone_counts

        for widget in self.left_box.winfo_children():
            widget.destroy()

        for widget in self.right_box.winfo_children():
            widget.destroy()

        # Etiqueta Presets
        ctk.CTkLabel(
            self.left_box,
            text="🏷️ Presets:",
            font=FONTS["body_bold"],
            text_color=TEXT_MUTED
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Botones de cada zona
        for z in zones_list:
            is_active = (z.lower() == selected_zone.lower())
            count = zone_counts.get(z, 0)
            btn_text = f"{z} ({count})"

            fg_col = ACCENT_BLUE if is_active else BG_INPUT
            hov_col = HOVER_BLUE if is_active else HOVER_SECONDARY

            ctk.CTkButton(
                self.left_box,
                text=btn_text,
                font=FONTS["caption_bold"],
                fg_color=fg_col,
                hover_color=hov_col,
                text_color=TEXT_PRIMARY,
                height=28,
                corner_radius=6,
                command=lambda val=z: self._select_zone(val)
            ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Encender Zona Activa
        act_count = zone_counts.get(selected_zone, 0)
        if selected_zone == "Todos":
            wake_text = f"⚡ Encender Todos ({act_count})"
        else:
            wake_text = f"⚡ Encender {selected_zone} ({act_count})"

        ctk.CTkButton(
            self.right_box,
            text=wake_text,
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=TEXT_PRIMARY,
            height=28,
            corner_radius=6,
            command=lambda: self.on_wake_zone(self._active_zone) if self.on_wake_zone else None
        ).pack(side=tk.RIGHT)

    def _select_zone(self, zone_name: str) -> None:
        self._active_zone = zone_name
        if self.on_zone_selected:
            self.on_zone_selected(zone_name)
