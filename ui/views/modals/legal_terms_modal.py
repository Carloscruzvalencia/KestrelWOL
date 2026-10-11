"""
Modal de Términos Legales y Exoneración de Responsabilidad (ui/views/modals/legal_terms_modal.py)
KestrelWOL - CustomTkinter
"""

import sys
import tkinter as tk
from typing import Callable, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    ACCENT_ROSE,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BG_INPUT,
    FONTS,
    HOVER_EMERALD,
    HOVER_ROSE,
    HOVER_SECONDARY,
    LEGAL_TERMS_FULL_TEXT,
    MODAL_SIZES,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


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
        self.title("⚖️ Términos de Uso, Seguridad Industrial y Exoneración Legal")
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        if self.is_first_run:
            # Si el usuario cierra con la 'X' de la ventana sin aceptar, cerrar toda la app
            self.protocol("WM_DELETE_WINDOW", self._reject_and_exit)

        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header,
            text="⚖️ Marco Normativo, Seguridad y Exoneración de Responsabilidad",
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

        # Cuadro de texto de solo lectura
        txt_box = ctk.CTkTextbox(
            self,
            font=FONTS["mono_log"],
            fg_color=BG_CONTAINER_DARK,
            text_color=TEXT_PRIMARY,
            corner_radius=8
        )
        txt_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))
        txt_box.insert("1.0", LEGAL_TERMS_FULL_TEXT)
        txt_box.configure(state="disabled")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=(0, 14))

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
                command=self._on_check_toggle
            )
            chk.pack(anchor="w", pady=(0, 10))

            btn_box = ctk.CTkFrame(footer, fg_color="transparent")
            btn_box.pack(fill=tk.X)

            ctk.CTkButton(
                btn_box,
                text="❌ Rechazar y Salir",
                font=FONTS["body_normal"],
                fg_color=ACCENT_ROSE,
                hover_color=HOVER_ROSE,
                text_color="#ffffff",
                command=self._reject_and_exit
            ).pack(side=tk.LEFT)

            # Botón desactivado por defecto con fondo neutro y texto legible
            self.btn_accept = ctk.CTkButton(
                btn_box,
                text="✅ Aceptar y Continuar",
                font=FONTS["body_bold"],
                fg_color=BG_INPUT,
                hover_color=HOVER_EMERALD,
                text_color="#94a3b8",
                state="disabled",
                command=self._accept
            )
            self.btn_accept.pack(side=tk.RIGHT)
        else:
            ctk.CTkButton(
                footer,
                text="Cerrar",
                font=FONTS["body_normal"],
                fg_color=BG_INPUT,
                hover_color=HOVER_SECONDARY,
                text_color=TEXT_PRIMARY,
                command=self.destroy
            ).pack(side=tk.RIGHT)

    def _on_check_toggle(self) -> None:
        if hasattr(self, "btn_accept"):
            if self.chk_var.get():
                self.btn_accept.configure(
                    state="normal",
                    fg_color=ACCENT_EMERALD,
                    text_color="#ffffff",
                    hover_color=HOVER_EMERALD
                )
            else:
                self.btn_accept.configure(
                    state="disabled",
                    fg_color=BG_INPUT,
                    text_color="#94a3b8"
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
