"""
Modal de Administración de IPs Ignoradas (ui/views/modals/ignored_modal.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    BG_CARD,
    BG_DARK,
    BG_INPUT,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_PRIMARY,
)
from services.storage_service import StorageService


class IgnoredModal(ctk.CTkToplevel):
    """
    Diálogo modal para visualizar y desbloquear IPs excluidas del escáner de red.
    """

    def __init__(
        self,
        parent,
        storage_service: Optional[StorageService] = None
    ):
        super().__init__(parent)
        self.storage = storage_service or StorageService()

        w, h = MODAL_SIZES["ignored_manager"]
        self.title("IPs Ignoradas")
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.load_list()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header,
            text="🚫 Dispositivos e IPs Ignoradas",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=14, pady=10)

        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        self.listbox = tk.Listbox(
            card,
            bg="#0f172a",
            fg=TEXT_PRIMARY,
            selectbackground="#3b82f6",
            selectforeground=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=10
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=(0, 14))

        ctk.CTkButton(
            footer,
            text="Cerrar",
            font=FONTS["body_normal"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            command=self.destroy
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            footer,
            text="✅ Dejar de Ignorar",
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=TEXT_PRIMARY,
            command=self._unignore_selected
        ).pack(side=tk.RIGHT)

    def load_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for ip in self.storage.load_ignored_ips():
            self.listbox.insert(tk.END, ip)

    def _unignore_selected(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        ip = self.listbox.get(sel[0])
        ignored = self.storage.load_ignored_ips()
        if ip in ignored:
            ignored.remove(ip)
            self.storage.save_ignored_ips(ignored)
            self.load_list()
            messagebox.showinfo("Desbloqueado", f"{ip} ha sido eliminada de la lista de ignorados.", parent=self)
