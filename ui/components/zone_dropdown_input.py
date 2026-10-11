"""
Componente Selector Desplegable de Zonas (ui/components/zone_dropdown_input.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Callable, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_BLUE,
    BG_CARD,
    BG_INPUT,
    FONTS,
    TEXT_PRIMARY,
)


class ZoneDropdownInput(ctk.CTkFrame):
    """
    Campo de entrada CustomTkinter con selector desplegable de zonas existentes:
    - Permite escribir libremente cualquier nombre de zona.
    - Botón desplegable [▾] que muestra todas las zonas activas.
    - Permite la selección con un clic sin necesidad de escribir.
    """

    def __init__(
        self,
        parent,
        get_zones_callback: Optional[Callable[[], List[str]]] = None,
        width: int = 140,
        height: int = 32,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color="transparent",
            width=width,
            height=height,
            **kwargs
        )
        self.get_zones_callback = get_zones_callback

        self.entry = ctk.CTkEntry(
            self,
            font=FONTS["body_normal"],
            height=height,
            fg_color=BG_CARD,
            border_color=BG_INPUT,
            border_width=1,
            text_color=TEXT_PRIMARY,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))

        self.btn_drop = ctk.CTkButton(
            self,
            text="▾",
            width=28,
            height=height,
            font=FONTS["body_bold"],
            fg_color=BG_CARD,
            hover_color=BG_INPUT,
            text_color="#38bdf8",
            border_color=BG_INPUT,
            border_width=1,
            command=self._show_dropdown
        )
        self.btn_drop.pack(side=tk.RIGHT)

    def get(self) -> str:
        return self.entry.get()

    def set(self, text: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    def delete(self, first: int, last: Optional[int] = None) -> None:
        self.entry.delete(first, last)

    def insert(self, index: int, string: str) -> None:
        self.entry.insert(index, string)

    def _show_dropdown(self) -> None:
        zones = []
        if callable(self.get_zones_callback):
            zones = self.get_zones_callback()
        if not zones:
            zones = ["Zona A", "Zona B"]

        menu = tk.Menu(
            self,
            tearoff=0,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            activebackground=ACCENT_BLUE,
            activeforeground=TEXT_PRIMARY,
            font=("Segoe UI", 9)
        )
        for z in zones:
            menu.add_command(
                label=f"📍 {z}",
                command=lambda val=z: self.set(val)
            )

        try:
            x = self.btn_drop.winfo_rootx()
            y = self.btn_drop.winfo_rooty() + self.btn_drop.winfo_height()
            menu.tk_popup(x, y)
        except Exception:
            pass
