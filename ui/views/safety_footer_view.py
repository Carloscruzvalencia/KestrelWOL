"""
Vista de Banner Inferior de Seguridad y EULA (ui/views/safety_footer_view.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

from core.config import (
    BG_CONTAINER_DARK,
    BG_INPUT,
    EULA_BANNER_TEXT,
    FONTS,
    HOVER_SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class SafetyFooterView(ctk.CTkFrame):
    """
    Banner inferior persistente que garantiza la visibilidad de la cláusula
    EULA y la normativa de seguridad laboral (Directiva 2006/42/CE & REBT).
    """

    def __init__(
        self,
        parent,
        on_open_terms: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=BG_CONTAINER_DARK,
            corner_radius=6,
            height=32,
            **kwargs
        )
        self.on_open_terms = on_open_terms
        self._build_ui()

    def _build_ui(self) -> None:
        lbl_eula = ctk.CTkLabel(
            self,
            text=EULA_BANNER_TEXT,
            font=FONTS["caption_normal"],
            text_color=TEXT_MUTED,
            anchor="w"
        )
        lbl_eula.pack(side=tk.LEFT, padx=12, pady=6)

        ctk.CTkButton(
            self,
            text="Ver Detalles Legales",
            font=FONTS["micro"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=22,
            corner_radius=4,
            command=lambda: self.on_open_terms() if self.on_open_terms else None
        ).pack(side=tk.RIGHT, padx=12, pady=6)
