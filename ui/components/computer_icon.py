"""
Componente Gráfico de Monitor de Red (ui/components/computer_icon.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Tuple
import customtkinter as ctk

from core.config import BG_CARD, STATUS_COLORS


class ComputerIconComponent(ctk.CTkCanvas):
    """
    Icono vectorial de monitor que refleja visualmente el estado del equipo:
    - 'online' (Encendido): marco verde con pantalla y tick (✔).
    - 'offline' (Desconectado): marco rojo con cruz (✖).
    - 'error' (Advertencia): marco ámbar con icono de atención (!).
    - 'pending' (En sondeo): marco pizarra con puntos suspensivos (⋯).
    """

    def __init__(
        self,
        parent,
        size: Tuple[int, int] = (54, 46),
        bg_color: str = BG_CARD,
        **kwargs
    ):
        super().__init__(
            parent,
            width=size[0],
            height=size[1],
            bg=bg_color,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self._current_state = "pending"
        self._bg_color = bg_color
        self.draw_icon("pending")

    def set_state(self, new_state: str) -> None:
        """Actualiza el estado gráfico solo si ha cambiado para optimizar el renderizado."""
        if self._current_state != new_state:
            self._current_state = new_state
            self.draw_icon(new_state)

    def draw_icon(self, state: str) -> None:
        self.delete("all")
        cfg = STATUS_COLORS.get(state, STATUS_COLORS["pending"])

        # Stand / Peana del monitor
        self.create_rectangle(24, 34, 30, 40, fill="#475569", outline="")
        self.create_rectangle(17, 40, 37, 43, fill="#64748b", outline="")

        # Carcasa y Pantalla
        fill_color = cfg["icon_fill"]
        outline_color = cfg["icon_outline"]

        if state == "online":
            self.create_rectangle(5, 5, 49, 34, fill=fill_color, outline=outline_color, width=2)
            self.create_line(16, 19, 24, 27, 38, 12, fill=outline_color, width=2.5, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        elif state == "offline":
            self.create_rectangle(5, 5, 49, 34, fill=fill_color, outline=outline_color, width=2)
            self.create_line(19, 12, 35, 26, fill=outline_color, width=2.5, capstyle=tk.ROUND)
            self.create_line(19, 26, 35, 12, fill=outline_color, width=2.5, capstyle=tk.ROUND)
        elif state == "error":
            self.create_rectangle(5, 5, 49, 34, fill=fill_color, outline=outline_color, width=2)
            self.create_polygon(27, 9, 16, 28, 38, 28, fill=outline_color, outline="#b45309")
            self.create_text(27, 21, text="!", fill="#1e293b", font=("Segoe UI", 10, "bold"))
        else:  # pending
            self.create_rectangle(5, 5, 49, 34, fill=fill_color, outline=outline_color, width=2)
            self.create_text(27, 19, text="⋯", fill="#94a3b8", font=("Segoe UI", 13, "bold"))
