"""
Vista de Cabecera y Barra de Acciones Globales (ui/views/header_view.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    APP_SUBTITLE,
    APP_TITLE,
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    BUTTON_PRIMARY_TEXT,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from ui.components.icons import get_icon


class HeaderView(ctk.CTkFrame):
    """
    Cabecera superior:
    - Título y descripción operativa de la aplicación.
    - Acciones secundarias monocromas (#1A1E26) + CTA primario único (#10B981).
    - Totalmente desacoplada: notifica al orquestador a través de callbacks.
    """

    def __init__(
        self,
        parent,
        on_open_terms: Optional[Callable[[], None]] = None,
        on_open_audit: Optional[Callable[[], None]] = None,
        on_wake_all: Optional[Callable[[], None]] = None,
        on_import_csv: Optional[Callable[[], None]] = None,
        on_export_csv: Optional[Callable[[], None]] = None,
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
        self.on_open_terms = on_open_terms
        self.on_open_audit = on_open_audit
        self.on_wake_all = on_wake_all
        self.on_import_csv = on_import_csv
        self.on_export_csv = on_export_csv

        self._build_ui()

    def _build_ui(self) -> None:
        title_box = ctk.CTkFrame(self, fg_color="transparent")
        title_box.pack(side=tk.LEFT, padx=16, pady=12)

        lbl_title = ctk.CTkLabel(
            title_box,
            text=APP_TITLE,
            font=FONTS["title_main"],
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text=APP_SUBTITLE,
            font=FONTS["caption_normal"],
            text_color=TEXT_MUTED,
            anchor="w"
        )
        lbl_sub.pack(anchor="w")

        # Botonera derecha
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(side=tk.RIGHT, padx=16, pady=12)

        sec_btn_kwargs = {
            "font": FONTS["caption_bold"],
            "fg_color": BG_BTN_SECONDARY,
            "hover_color": HOVER_SECONDARY,
            "border_width": 1,
            "border_color": BG_BORDER_BUTTON,
            "text_color": TEXT_SECONDARY,
            "height": 32,
            "corner_radius": UI_RADIUS,
        }

        # Botón Importar CSV
        ctk.CTkButton(
            btn_box,
            text="Importar CSV",
            image=get_icon("upload", TEXT_SECONDARY, 14),
            compound="left",
            command=lambda: self.on_import_csv() if self.on_import_csv else None,
            **sec_btn_kwargs
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Exportar CSV
        ctk.CTkButton(
            btn_box,
            text="Exportar CSV",
            image=get_icon("download", TEXT_SECONDARY, 14),
            compound="left",
            command=lambda: self.on_export_csv() if self.on_export_csv else None,
            **sec_btn_kwargs
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Términos y Normativas
        ctk.CTkButton(
            btn_box,
            text="Términos",
            image=get_icon("shield", TEXT_SECONDARY, 14),
            compound="left",
            command=lambda: self.on_open_terms() if self.on_open_terms else None,
            **sec_btn_kwargs
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Registro de Auditoría
        ctk.CTkButton(
            btn_box,
            text="Auditoría",
            image=get_icon("file", TEXT_SECONDARY, 14),
            compound="left",
            command=lambda: self.on_open_audit() if self.on_open_audit else None,
            **sec_btn_kwargs
        ).pack(side=tk.LEFT, padx=(0, 8))

        # Único botón CTA primario global (Verde Esmeralda)
        ctk.CTkButton(
            btn_box,
            text="ENCENDER TODOS",
            image=get_icon("power", BUTTON_PRIMARY_TEXT, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=BUTTON_PRIMARY_TEXT,
            height=32,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_wake_all() if self.on_wake_all else None
        ).pack(side=tk.LEFT)
