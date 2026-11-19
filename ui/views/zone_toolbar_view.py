"""
Vista de Barra de Presets de Zonas (ui/views/zone_toolbar_view.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from typing import Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_ROW,
    FONTS,
    HOVER_SECONDARY,
    TEXT_DISABLED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from ui.components.icons import get_icon


class ZoneToolbarView(ctk.CTkFrame):
    """
    Barra horizontal con selector de presets de zonas y botón rápido de encendido:
    - Botones dinámicos: [Todos (N)], [Zona A (M)], [Zona B (K)]...
    - Botón de visibilidad global de red y encendido por zona contextual.
    """

    def __init__(
        self,
        parent,
        on_zone_selected: Optional[Callable[[str], None]] = None,
        on_wake_zone: Optional[Callable[[str], None]] = None,
        on_toggle_network: Optional[Callable[[], bool]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )
        self.on_zone_selected = on_zone_selected
        self.on_wake_zone = on_wake_zone
        self.on_toggle_network = on_toggle_network

        self._active_zone = "Todos"
        self._zone_counts: Dict[str, int] = {"Todos": 0}
        self._network_visible = False

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
            text="  ZONAS",
            image=get_icon("tag", TEXT_DISABLED, 13),
            compound="left",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Botones de cada zona
        for z in zones_list:
            is_active = (z.lower() == selected_zone.lower())
            count = zone_counts.get(z, 0)
            btn_text = f"{z} ({count})"

            fg_col = BG_ROW if is_active else BG_BTN_SECONDARY
            border_col = ACCENT_EMERALD if is_active else BG_BORDER
            txt_col = TEXT_PRIMARY if is_active else TEXT_MUTED

            ctk.CTkButton(
                self.left_box,
                text=btn_text,
                font=FONTS["caption_bold"],
                fg_color=fg_col,
                hover_color=HOVER_SECONDARY,
                border_width=1,
                border_color=border_col,
                text_color=txt_col,
                width=0,
                height=28,
                corner_radius=UI_RADIUS,
                command=lambda val=z: self._select_zone(val)
            ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Encender Zona Activa
        act_count = zone_counts.get(selected_zone, 0)
        if selected_zone == "Todos":
            wake_text = f"Encender Todos ({act_count})"
        else:
            wake_text = f"Encender {selected_zone} ({act_count})"

        ctk.CTkButton(
            self.right_box,
            text=wake_text,
            image=get_icon("power", ACCENT_EMERALD, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color="#102820",
            hover_color="#16382D",
            border_width=1,
            border_color="#1D4D3D",
            text_color=ACCENT_EMERALD,
            width=0,
            height=28,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_wake_zone(self._active_zone) if self.on_wake_zone else None
        ).pack(side=tk.RIGHT)

        # Botón Mostrar/Ocultar Red (IP y MAC) Globalmente
        toggle_label = "Ocultar Red" if self._network_visible else "Ver Red"
        toggle_icon = "eye_off" if self._network_visible else "eye"
        self.btn_toggle_network = ctk.CTkButton(
            self.right_box,
            text=toggle_label,
            image=get_icon(toggle_icon, TEXT_SECONDARY, 14),
            compound="left",
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            width=0,
            height=28,
            corner_radius=UI_RADIUS,
            command=self._handle_toggle_network
        )
        self.btn_toggle_network.pack(side=tk.RIGHT, padx=(0, 8))

    def _handle_toggle_network(self) -> None:
        if self.on_toggle_network:
            new_state = self.on_toggle_network()
            self._network_visible = bool(new_state)
            if hasattr(self, "btn_toggle_network") and self.btn_toggle_network:
                self.btn_toggle_network.configure(
                    text="Ocultar Red" if self._network_visible else "Ver Red",
                    image=get_icon("eye_off" if self._network_visible else "eye", TEXT_SECONDARY, 14)
                )

    def _select_zone(self, zone_name: str) -> None:
        self._active_zone = zone_name
        if self.on_zone_selected:
            self.on_zone_selected(zone_name)
