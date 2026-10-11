"""
Modal de Edición de Parámetros de Dispositivo (ui/views/modals/device_edit_modal.py)
KestrelWOL - CustomTkinter
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_BLUE,
    BG_CARD,
    BG_DARK,
    BG_INPUT,
    FONTS,
    HOVER_BLUE,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_MUTED,
    TEXT_PRIMARY,
)
from services.wol_service import WolService
from ui.components.zone_dropdown_input import ZoneDropdownInput


class DeviceEditModal(ctk.CTkToplevel):
    """
    Diálogo modal para editar Nombre, IP, MAC y reasignar Zona con selector desplegable.
    """

    def __init__(
        self,
        parent,
        machine: Dict[str, Any],
        get_zones_callback: Optional[Callable[[], List[str]]] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        super().__init__(parent)
        self.machine = machine
        self.get_zones_callback = get_zones_callback
        self.on_save = on_save

        w, h = MODAL_SIZES["device_edit"]
        self.title(f"Editar Dispositivo: {machine.get('name')}")
        self.geometry(f"{w}x{h}")
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        ctk.CTkLabel(
            header,
            text="✏️ Modificar Parámetros del Equipo",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            header,
            text=f"Puesto: {self.machine.get('name')} | IP: {self.machine.get('ip')}",
            font=FONTS["caption_normal"],
            text_color=TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        form.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        # 1. Nombre
        ctk.CTkLabel(form, text="Nombre del Equipo:", font=FONTS["body_bold"], text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 2))
        self.entry_name = ctk.CTkEntry(form, font=FONTS["body_normal"], height=30, fg_color=BG_DARK, border_color=BG_INPUT, border_width=1)
        self.entry_name.insert(0, self.machine.get("name", ""))
        self.entry_name.pack(fill=tk.X, padx=14, pady=(0, 8))

        # 2. IP
        ctk.CTkLabel(form, text="Dirección IP:", font=FONTS["body_bold"], text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(0, 2))
        self.entry_ip = ctk.CTkEntry(form, font=FONTS["body_normal"], height=30, fg_color=BG_DARK, border_color=BG_INPUT, border_width=1)
        self.entry_ip.insert(0, self.machine.get("ip", ""))
        self.entry_ip.pack(fill=tk.X, padx=14, pady=(0, 8))

        # 3. MAC
        ctk.CTkLabel(form, text="Dirección MAC:", font=FONTS["body_bold"], text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(0, 2))
        self.entry_mac = ctk.CTkEntry(form, font=FONTS["body_normal"], height=30, fg_color=BG_DARK, border_color=BG_INPUT, border_width=1)
        self.entry_mac.insert(0, self.machine.get("mac", ""))
        self.entry_mac.pack(fill=tk.X, padx=14, pady=(0, 8))

        # 4. Zona
        ctk.CTkLabel(form, text="Zona / Sala:", font=FONTS["body_bold"], text_color=TEXT_MUTED).pack(anchor="w", padx=14, pady=(0, 2))
        self.entry_zone = ZoneDropdownInput(form, get_zones_callback=self.get_zones_callback, height=30)
        self.entry_zone.set(self.machine.get("zone", "General"))
        self.entry_zone.pack(fill=tk.X, padx=14, pady=(0, 10))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill=tk.X, padx=16, pady=(0, 14))

        ctk.CTkButton(
            footer,
            text="Cancelar",
            font=FONTS["body_normal"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            command=self.destroy
        ).pack(side=tk.LEFT)

        ctk.CTkButton(
            footer,
            text="💾 Guardar Cambios",
            font=FONTS["body_bold"],
            fg_color=ACCENT_BLUE,
            hover_color=HOVER_BLUE,
            text_color=TEXT_PRIMARY,
            command=self._save
        ).pack(side=tk.RIGHT)

    def _save(self) -> None:
        name = self.entry_name.get().strip()
        ip = self.entry_ip.get().strip()
        mac = self.entry_mac.get().strip()
        zone = self.entry_zone.get().strip() or "General"

        if not name or not ip or not mac:
            messagebox.showwarning("Campos Requeridos", "Por favor completa Nombre, IP y MAC.", parent=self)
            return

        if not WolService.validate_ip(ip):
            messagebox.showerror("IP Inválida", f"La dirección IP '{ip}' no cumple con el formato IPv4 estándar.", parent=self)
            return

        if not WolService.validate_mac(mac):
            messagebox.showerror("MAC Inválida", f"La dirección MAC '{mac}' no tiene un formato válido.", parent=self)
            return

        updated = dict(self.machine)
        updated["name"] = name
        updated["ip"] = ip
        updated["mac"] = mac
        updated["zone"] = zone

        self.destroy()
        if self.on_save:
            self.on_save(updated)
