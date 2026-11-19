"""
Vista de Banner Inferior de Seguridad y EULA (ui/views/safety_footer_view.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

from core.config import (
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    EULA_BANNER_TEXT,
    FONTS,
    HOVER_SECONDARY,
    TEXT_DISABLED,
    TEXT_MUTED,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from ui.components.icons import get_icon


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
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS,
            height=34,
            **kwargs
        )
        self.on_open_terms = on_open_terms
        self._build_ui()

    def _build_ui(self) -> None:
        lbl_eula = ctk.CTkLabel(
            self,
            text=f"  {EULA_BANNER_TEXT}",
            image=get_icon("shield", TEXT_DISABLED, 13),
            compound="left",
            font=FONTS["caption_normal"],
            text_color=TEXT_MUTED,
            anchor="w"
        )
        lbl_eula.pack(side=tk.LEFT, padx=12, pady=6)

        ctk.CTkButton(
            self,
            text="Ver Detalles Legales",
            font=FONTS["micro"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            height=24,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_open_terms() if self.on_open_terms else None
        ).pack(side=tk.RIGHT, padx=12, pady=6)
