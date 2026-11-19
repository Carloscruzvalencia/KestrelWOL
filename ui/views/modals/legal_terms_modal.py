"""
Modal de Términos Legales y Exoneración de Responsabilidad (ui/views/modals/legal_terms_modal.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import sys
import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    ACCENT_ROSE,
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BUTTON_PRIMARY_TEXT,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    LEGAL_TERMS_FULL_TEXT,
    MODAL_SIZES,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from ui.components.icons import get_icon


class LegalTermsModal(ctk.CTkToplevel):
    """
    Ventana modal informativa y de aceptación de Términos de Uso,
    Normativa Industrial (Directiva 2006/42/CE & REBT) y Exoneración Civil 'AS IS'.
    """

    def __init__(
        self,
        parent,
        is_first_run: bool = False,
        on_accept: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.is_first_run = is_first_run
        self.on_accept = on_accept

        w, h = MODAL_SIZES["legal_terms"]
        self.title("Términos de Uso, Seguridad Industrial y Exoneración Legal")
        self.geometry(f"{w}x{h}")
        self.minsize(w, h)
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        if self.is_first_run:
            # Si el usuario cierra con la 'X' de la ventana sin aceptar, cerrar toda la app
            self.protocol("WM_DELETE_WINDOW", self._reject_and_exit)

        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header,
            text="  Marco Normativo, Seguridad y Exoneración de Responsabilidad",
            image=get_icon("shield", TEXT_PRIMARY, 15),
            compound="left",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            header,
            text="KestrelWOL - Cumplimiento Industrial y Operativo",
            font=FONTS["caption_normal"],
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 14))

        if self.is_first_run:
            self.chk_var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(
                footer,
                text=" He leído, comprendo y acepto los términos de uso y las normas de seguridad laboral",
                variable=self.chk_var,
                font=FONTS["body_bold"],
                text_color=TEXT_PRIMARY,
                fg_color=ACCENT_EMERALD,
                hover_color=HOVER_EMERALD,
                border_color=BG_BORDER_BUTTON,
                corner_radius=4,
                command=self._on_check_toggle
            )
            chk.pack(anchor="w", pady=(0, 10))

            btn_box = ctk.CTkFrame(footer, fg_color="transparent")
            btn_box.pack(fill=tk.X)

            ctk.CTkButton(
                btn_box,
                text="Rechazar y Salir",
                image=get_icon("close", TEXT_MUTED, 14),
                compound="left",
                font=FONTS["body_normal"],
                fg_color=BG_BTN_SECONDARY,
                hover_color=ACCENT_ROSE,
                border_width=1,
                border_color=BG_BORDER_BUTTON,
                text_color=TEXT_MUTED,
                width=0,
                height=30,
                corner_radius=UI_RADIUS,
                command=self._reject_and_exit
            ).pack(side=tk.LEFT)

            self.btn_accept = ctk.CTkButton(
                btn_box,
                text="Aceptar y Continuar",
                image=get_icon("check", TEXT_MUTED, 14),
                compound="left",
                font=FONTS["body_bold"],
                fg_color=BG_BTN_SECONDARY,
                hover_color=HOVER_EMERALD,
                border_width=1,
                border_color=BG_BORDER_BUTTON,
                text_color=TEXT_MUTED,
                width=0,
                height=30,
                corner_radius=UI_RADIUS,
                state="disabled",
                command=self._accept
            )
            self.btn_accept.pack(side=tk.RIGHT)
        else:
            ctk.CTkButton(
                footer,
                text="Cerrar",
                font=FONTS["body_normal"],
                fg_color=BG_BTN_SECONDARY,
                hover_color=HOVER_SECONDARY,
                border_width=1,
                border_color=BG_BORDER_BUTTON,
                text_color=TEXT_SECONDARY,
                width=0,
                height=30,
                corner_radius=UI_RADIUS,
                command=self.destroy
            ).pack(side=tk.RIGHT)

        # Cuadro de texto de solo lectura
        txt_box = ctk.CTkTextbox(
            self,
            font=FONTS["mono_log"],
            fg_color=BG_CONTAINER_DARK,
            border_width=1,
            border_color=BG_BORDER,
            text_color=TEXT_SECONDARY,
            corner_radius=UI_RADIUS
        )
        txt_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))
        txt_box.insert("1.0", LEGAL_TERMS_FULL_TEXT)
        txt_box.configure(state="disabled")

    def _on_check_toggle(self) -> None:
        if hasattr(self, "btn_accept"):
            if self.chk_var.get():
                self.btn_accept.configure(
                    state="normal",
                    fg_color=ACCENT_EMERALD,
                    text_color=BUTTON_PRIMARY_TEXT,
                    border_color=ACCENT_EMERALD,
                    image=get_icon("check", BUTTON_PRIMARY_TEXT, 14),
                    hover_color=HOVER_EMERALD
                )
            else:
                self.btn_accept.configure(
                    state="disabled",
                    fg_color=BG_BTN_SECONDARY,
                    border_color=BG_BORDER_BUTTON,
                    image=get_icon("check", TEXT_MUTED, 14),
                    text_color=TEXT_MUTED
                )

    def _reject_and_exit(self) -> None:
        """Cierra la aplicación por completo si no se aceptan los términos legales."""
        if self.master:
            try:
                self.master.destroy()
            except Exception:
                pass
        sys.exit(0)

    def _accept(self) -> None:
        if self.on_accept:
            self.on_accept()
        self.destroy()
