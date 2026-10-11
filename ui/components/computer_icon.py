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
        size: Tuple[int, int] = (48, 42),
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
        self._size = size
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

        w, h = self._size

        # Margen de seguridad estricto para evitar recortes del trazo en el borde del Canvas
        pad_x = 4
        pad_top = 4
        screen_w = w - (2 * pad_x)
        screen_h = int(h * 0.58)

        x1 = pad_x
        y1 = pad_top
        x2 = x1 + screen_w
        y2 = y1 + screen_h

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # Stand / Peana del monitor
        stand_w = 6
        stand_top = y2
        stand_bot = min(h - 5, stand_top + 6)
        self.create_rectangle(
            cx - stand_w // 2, stand_top,
            cx + stand_w // 2, stand_bot,
            fill="#475569", outline=""
        )

        base_w = int(screen_w * 0.52)
        base_h = 3
        self.create_rectangle(
            cx - base_w // 2, stand_bot,
            cx + base_w // 2, stand_bot + base_h,
            fill="#64748b", outline=""
        )

        # Carcasa y Pantalla (marco cerrado de 4 lados garantizado)
        fill_color = cfg["icon_fill"]
        outline_color = cfg["icon_outline"]
        self.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=2)

        # Símbolos interiores centrados
        if state == "online":
            self.create_line(
                cx - 7, cy,
                cx - 2, cy + 5,
                cx + 7, cy - 4,
                fill=outline_color,
                width=2.5,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )
        elif state == "offline":
            offset = 5
            self.create_line(cx - offset, cy - offset, cx + offset, cy + offset, fill=outline_color, width=2.5, capstyle=tk.ROUND)
            self.create_line(cx - offset, cy + offset, cx + offset, cy - offset, fill=outline_color, width=2.5, capstyle=tk.ROUND)
        elif state == "error":
            poly = [cx, cy - 6, cx - 7, cy + 6, cx + 7, cy + 6]
            self.create_polygon(poly, fill=outline_color, outline="#b45309")
            self.create_text(cx, cy + 1, text="!", fill="#1e293b", font=("Segoe UI", 8, "bold"))
        else:  # pending
            self.create_text(cx, cy, text="⋯", fill="#94a3b8", font=("Segoe UI", 11, "bold"))
