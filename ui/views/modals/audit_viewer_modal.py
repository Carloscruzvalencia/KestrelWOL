"""
Modal de Registro de Auditoría Forense (ui/views/modals/audit_viewer_modal.py)
Cumplimiento: Directiva NIS 2 y Esquema Nacional de Seguridad (ENS)
"""

import tkinter as tk
from typing import Optional
import customtkinter as ctk

from core.config import (
    AUDIT_LOG_FILE,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BG_INPUT,
    FONTS,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_MUTED,
    TEXT_PRIMARY,
)
from services.audit_service import AuditService


class AuditViewerModal(ctk.CTkToplevel):
    """
    Visor interactivo del registro local audit.log:
    - Lectura inmutable protegida contra bloqueos.
    - Botón de refresco instantáneo.
    - Cumplimiento de trazabilidad NIS 2 / ENS.
    """

    def __init__(self, parent, audit_service: Optional[AuditService] = None):
        super().__init__(parent)
        self.audit = audit_service or AuditService()

        w, h = MODAL_SIZES["audit_viewer"]
        self.title("📋 Registro de Auditoría y Trazabilidad (NIS 2 / ENS)")
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.load_log()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header,
            text="📋 Registro Local de Auditoría (audit.log)",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=14, pady=10)

        ctk.CTkButton(
            header,
            text="🔄 Refrescar",
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=28,
            command=self.load_log
        ).pack(side=tk.RIGHT, padx=14, pady=10)

        self.txt_log = ctk.CTkTextbox(
            self,
            font=FONTS["mono_log"],
            fg_color=BG_CONTAINER_DARK,
            text_color="#38bdf8",
            corner_radius=8
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=(0, 14))

        ctk.CTkLabel(
            footer,
            text=f"Ruta: {AUDIT_LOG_FILE}",
            font=FONTS["caption_normal"],
            text_color=TEXT_MUTED
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            footer,
            text="Cerrar",
            font=FONTS["body_normal"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            command=self.destroy
        ).pack(side=tk.RIGHT)

    def load_log(self) -> None:
        lines = self.audit.read_last_entries(max_lines=200)
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", tk.END)
        if lines:
            self.txt_log.insert(tk.END, "".join(lines))
            self.txt_log.see(tk.END)
        else:
            self.txt_log.insert(tk.END, "El archivo audit.log aún no contiene registros.\n")
        self.txt_log.configure(state="disabled")
