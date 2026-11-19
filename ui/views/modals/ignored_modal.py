"""
Modal de Administración de IPs Ignoradas (ui/views/modals/ignored_modal.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional
import customtkinter as ctk

from core.config import (
    ACCENT_EMERALD,
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BG_ROW,
    BUTTON_PRIMARY_TEXT,
    FONTS,
    HOVER_EMERALD,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from services.storage_service import StorageService
from ui.components.icons import get_icon


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
            text="  Dispositivos e IPs Ignoradas",
            image=get_icon("eye_off", TEXT_PRIMARY, 15),
            compound="left",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=14, pady=10)

        card = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        self.listbox = tk.Listbox(
            card,
            bg=BG_CONTAINER_DARK,
            fg=TEXT_PRIMARY,
            selectbackground=BG_ROW,
            selectforeground=ACCENT_EMERALD,
            font=FONTS["mono_data"],
            bd=0,
            highlightthickness=1,
            highlightbackground=BG_BORDER,
            highlightcolor=BG_BORDER,
            activestyle="none"
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=(0, 14))

        ctk.CTkButton(
            footer,
            text="Cerrar",
            font=FONTS["body_normal"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            height=30,
            corner_radius=UI_RADIUS,
            command=self.destroy
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            footer,
            text="Dejar de Ignorar",
            image=get_icon("check", BUTTON_PRIMARY_TEXT, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=BUTTON_PRIMARY_TEXT,
            height=30,
            corner_radius=UI_RADIUS,
            command=self._unignore_selected
        ).pack(side=tk.RIGHT)

    def load_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for ip in self.storage.load_ignored_ips():
            self.listbox.insert(tk.END, f"  {ip}")

    def _unignore_selected(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            return
        ip = self.listbox.get(sel[0]).strip()
        ignored = self.storage.load_ignored_ips()
        if ip in ignored:
            ignored.remove(ip)
            self.storage.save_ignored_ips(ignored)
            self.load_list()
            messagebox.showinfo("Desbloqueado", f"{ip} ha sido eliminada de la lista de ignorados.", parent=self)
