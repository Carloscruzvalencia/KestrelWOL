"""
Modal de Escaneo de Red Local (ui/views/modals/scanner_modal.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Optional
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
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from services.scanner_service import ScannerService
from services.storage_service import StorageService
from ui.components.icons import get_icon


class ScannerModal(ctk.CTkToplevel):
    """
    Diálogo modal para escanear y descubrir dispositivos en la red LAN activa.
    """

    def __init__(
        self,
        parent,
        scanner_service: Optional[ScannerService] = None,
        storage_service: Optional[StorageService] = None,
        on_select_device: Optional[Callable[[str, str, str], None]] = None,
        on_open_ignored: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.scanner = scanner_service or ScannerService()
        self.storage = storage_service or StorageService()
        self.on_select_device = on_select_device
        self.on_open_ignored = on_open_ignored

        w, h = MODAL_SIZES["scanner"]
        self.title("Escáner de Red Local Activa")
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self.start_scan()

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
            text="  Dispositivos Detectados en la Red Local",
            image=get_icon("search", TEXT_PRIMARY, 15),
            compound="left",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=14, pady=10)

        ctk.CTkButton(
            header,
            text="Re-escanear",
            image=get_icon("refresh", TEXT_SECONDARY, 14),
            compound="left",
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            height=28,
            corner_radius=UI_RADIUS,
            command=self.start_scan
        ).pack(side=tk.RIGHT, padx=14, pady=10)

        # Contenedor de la tabla
        tree_frame = ctk.CTkFrame(
            self,
            fg_color=BG_CARD,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # Estilo ttk para la tabla (paleta Obsidian + Consolas)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Scanner.Treeview",
            background=BG_CONTAINER_DARK,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_CONTAINER_DARK,
            borderwidth=0,
            font=FONTS["mono_data"],
            rowheight=28
        )
        style.map(
            "Scanner.Treeview",
            background=[("selected", BG_ROW)],
            foreground=[("selected", ACCENT_EMERALD)]
        )
        style.configure(
            "Scanner.Treeview.Heading",
            background=BG_CARD,
            foreground=TEXT_MUTED,
            relief="flat",
            borderwidth=0,
            font=FONTS["caption_bold"]
        )

        cols = ("ip", "mac", "host")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", style="Scanner.Treeview")
        self.tree.heading("ip", text="DIRECCIÓN IP")
        self.tree.heading("mac", text="DIRECCIÓN MAC")
        self.tree.heading("host", text="NOMBRE / HOST")

        self.tree.column("ip", width=150, anchor="center")
        self.tree.column("mac", width=190, anchor="center")
        self.tree.column("host", width=260, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=(0, 14))

        sec_btn_kwargs = {
            "fg_color": BG_BTN_SECONDARY,
            "hover_color": HOVER_SECONDARY,
            "border_width": 1,
            "border_color": BG_BORDER_BUTTON,
            "text_color": TEXT_SECONDARY,
            "height": 30,
            "corner_radius": UI_RADIUS,
        }

        ctk.CTkButton(
            footer,
            text="Cerrar",
            font=FONTS["body_normal"],
            command=self.destroy,
            **sec_btn_kwargs
        ).pack(side=tk.LEFT)

        if self.on_open_ignored:
            ctk.CTkButton(
                footer,
                text="Gestionar Ignorados",
                image=get_icon("sliders", TEXT_SECONDARY, 14),
                compound="left",
                font=FONTS["caption_bold"],
                command=self.on_open_ignored,
                **sec_btn_kwargs
            ).pack(side=tk.LEFT, padx=(8, 0))

        ctk.CTkButton(
            footer,
            text="Ignorar Seleccionado",
            image=get_icon("eye_off", TEXT_SECONDARY, 14),
            compound="left",
            font=FONTS["caption_bold"],
            command=self._ignore_selected,
            **sec_btn_kwargs
        ).pack(side=tk.RIGHT, padx=(6, 0))

        ctk.CTkButton(
            footer,
            text="Seleccionar Equipo",
            image=get_icon("check", BUTTON_PRIMARY_TEXT, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=BUTTON_PRIMARY_TEXT,
            height=30,
            corner_radius=UI_RADIUS,
            command=self._use_selected
        ).pack(side=tk.RIGHT)

    def start_scan(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        def on_done(devices: List[Dict[str, str]]):
            self.after(0, lambda: self._populate(devices))

        def on_err(msg: str):
            self.after(0, lambda: messagebox.showerror("Error de Escáner", msg, parent=self))

        self.scanner.scan_arp_async(on_complete=on_done, on_error=on_err)

    def _populate(self, devices: List[Dict[str, str]]) -> None:
        for dev in devices:
            self.tree.insert("", tk.END, values=(dev.get("ip", ""), dev.get("mac", ""), dev.get("host", "")))

    def _use_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Selección", "Por favor selecciona un dispositivo de la lista.", parent=self)
            return
        vals = self.tree.item(sel[0])["values"]
        if vals and len(vals) >= 3:
            ip, mac, host = str(vals[0]), str(vals[1]), str(vals[2])
            self.destroy()
            if self.on_select_device:
                self.on_select_device(ip, mac, host)

    def _ignore_selected(self) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        if vals:
            ip = str(vals[0])
            ignored = self.storage.load_ignored_ips()
            if ip not in ignored:
                ignored.append(ip)
                self.storage.save_ignored_ips(ignored)
                self.tree.delete(sel[0])
                messagebox.showinfo("IP Ignorada", f"La IP {ip} ha sido agregada a la lista de ignorados.", parent=self)
