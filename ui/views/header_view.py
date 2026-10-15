"""
Vista de Cabecera y Barra de Acciones Globales (ui/views/header_view.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    APP_SUBTITLE,
    APP_TITLE,
    BG_CARD,
    BG_INPUT,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class HeaderView(ctk.CTkFrame):
    """
    Cabecera superior:
    - Título y descripción operativa de la aplicación.
    - Botones de acción globales (Términos legales, Auditoría, Encendido Masivo).
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
            corner_radius=8,
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

        # Botón Importar CSV
        ctk.CTkButton(
            btn_box,
            text="📥 Importar CSV",
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=32,
            command=lambda: self.on_import_csv() if self.on_import_csv else None
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Exportar CSV
        ctk.CTkButton(
            btn_box,
            text="📤 Exportar CSV",
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=32,
            command=lambda: self.on_export_csv() if self.on_export_csv else None
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Términos y Normativas
        ctk.CTkButton(
            btn_box,
            text="⚖️ Términos",
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=32,
            command=lambda: self.on_open_terms() if self.on_open_terms else None
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Registro de Auditoría
        ctk.CTkButton(
            btn_box,
            text="📋 Auditoría",
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=32,
            command=lambda: self.on_open_audit() if self.on_open_audit else None
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Botón Encender Todos
        ctk.CTkButton(
            btn_box,
            text="⚡ ENCENDER TODOS",
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=TEXT_PRIMARY,
            height=32,
            command=lambda: self.on_wake_all() if self.on_wake_all else None
        ).pack(side=tk.LEFT)
