"""
Modal de Control Remoto, Conexión Rápida y Diagnóstico de Servicios
(ui/views/modals/remote_control_modal.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
"""

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_BLUE,
    ACCENT_EMERALD,
    ACCENT_ROSE,
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BTN_SECONDARY,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BG_ROW,
    FONTS,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_DISABLED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from services.audit_service import AuditService
from services.system_service import SystemService
from ui.components.icons import get_icon, get_status_dot


class RemoteControlModal(ctk.CTkToplevel):
    """
    Diálogo para gestión remota del puesto:
    - Comprobación en vivo de servicios (RDP, SSH).
    - Conexión rápida directa con un clic (RDP mstsc, consola SSH).
    - Apagado y reinicio remoto controlado con aviso preventivo (Graceful Shutdown).
    """

    def __init__(self, parent, machine: Dict[str, Any], audit_service: Optional[AuditService] = None):
        super().__init__(parent)
        self.machine = machine
        self.audit = audit_service or AuditService()

        w, h = MODAL_SIZES.get("remote_control", (580, 560))
        self.title(f"Control y Conexión Remota - {machine.get('name', 'Puesto')}")
        self.geometry(f"{w}x{h}")
        self.minsize(w, h)
        self.configure(fg_color=BG_DARK)

        self.transient(parent)
        self.grab_set()

        self._service_labels: Dict[str, ctk.CTkLabel] = {}
        self._build_ui()
        self._start_service_scan()

    def _build_ui(self) -> None:
        ip = self.machine.get("ip", "N/A")
        mac = self.machine.get("mac", "N/A")
        name = self.machine.get("name", "Equipo")
        zone = self.machine.get("zone", "General")

        card_kwargs = {
            "fg_color": BG_CARD,
            "border_width": 1,
            "border_color": BG_BORDER,
            "corner_radius": UI_RADIUS,
        }

        # 1. Cabecera con info del equipo
        header = ctk.CTkFrame(self, **card_kwargs)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        top_info = ctk.CTkFrame(header, fg_color="transparent")
        top_info.pack(fill=tk.X, padx=14, pady=10)

        ctk.CTkLabel(
            top_info,
            text=f"  {name}",
            image=get_icon("monitor", TEXT_PRIMARY, 16),
            compound="left",
            font=FONTS["title_main"],
            text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        ctk.CTkLabel(
            top_info,
            text=f"{zone}  |  IP: {ip}  |  MAC: {mac}",
            font=FONTS["mono_log"],
            text_color=TEXT_MUTED
        ).pack(side=tk.RIGHT)

        # 2. Diagnóstico de Puertos y Servicios Remotos
        services_card = ctk.CTkFrame(self, **card_kwargs)
        services_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            services_card,
            text="  DIAGNÓSTICO DE SERVICIOS DE RED",
            image=get_icon("search", TEXT_DISABLED, 13),
            compound="left",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED
        ).pack(anchor="w", padx=14, pady=(10, 6))

        grid_frame = ctk.CTkFrame(
            services_card,
            fg_color=BG_CONTAINER_DARK,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        grid_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        services_def = [
            ("rdp", "monitor", "RDP (Puerto 3389 - Escritorio Remoto)"),
            ("ssh", "terminal", "SSH (Puerto 22 - Consola Shell Segura)"),
        ]

        for srv_key, icon_name, srv_label in services_def:
            row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            row_frame.pack(fill=tk.X, padx=10, pady=6)

            ctk.CTkLabel(
                row_frame,
                text=f"  {srv_label}",
                image=get_icon(icon_name, TEXT_SECONDARY, 14),
                compound="left",
                font=FONTS["body_normal"],
                text_color=TEXT_PRIMARY
            ).pack(side=tk.LEFT)

            lbl_status = ctk.CTkLabel(
                row_frame,
                text="  COMPROBANDO",
                image=get_status_dot(ACCENT_BLUE, 6),
                compound="left",
                font=FONTS["micro"],
                text_color=TEXT_MUTED,
                fg_color=BG_ROW,
                corner_radius=UI_RADIUS,
                padx=8,
                pady=2
            )
            lbl_status.pack(side=tk.RIGHT)
            self._service_labels[srv_key] = lbl_status

        # 3. Conexión Rápida
        conn_card = ctk.CTkFrame(self, **card_kwargs)
        conn_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            conn_card,
            text="CONEXIÓN INMEDIATA",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED
        ).pack(anchor="w", padx=14, pady=(10, 6))

        btn_conn_box = ctk.CTkFrame(conn_card, fg_color="transparent")
        btn_conn_box.pack(fill=tk.X, padx=14, pady=(0, 12))

        btn_sec_kwargs = {
            "font": FONTS["body_bold"],
            "fg_color": BG_BTN_SECONDARY,
            "hover_color": HOVER_SECONDARY,
            "border_width": 1,
            "border_color": BG_BORDER_BUTTON,
            "text_color": TEXT_SECONDARY,
            "height": 32,
            "corner_radius": UI_RADIUS,
        }

        ctk.CTkButton(
            btn_conn_box,
            text="Iniciar Sesión RDP",
            image=get_icon("monitor", TEXT_SECONDARY, 14),
            compound="left",
            command=self._launch_rdp,
            **btn_sec_kwargs
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        ctk.CTkButton(
            btn_conn_box,
            text="Abrir Consola SSH",
            image=get_icon("terminal", TEXT_SECONDARY, 14),
            compound="left",
            command=self._launch_ssh,
            **btn_sec_kwargs
        ).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 4. Gestión de Energía (Graceful Shutdown)
        power_card = ctk.CTkFrame(self, **card_kwargs)
        power_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            power_card,
            text="CONTROL DE ENERGÍA REMOTO (APAGADO / REINICIO)",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED
        ).pack(anchor="w", padx=14, pady=(10, 6))

        power_btn_box = ctk.CTkFrame(power_card, fg_color="transparent")
        power_btn_box.pack(fill=tk.X, padx=14, pady=(0, 12))

        ctk.CTkButton(
            power_btn_box,
            text="Apagar Remotamente (30s)",
            image=get_icon("power_off", TEXT_MUTED, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=ACCENT_ROSE,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_MUTED,
            height=32,
            corner_radius=UI_RADIUS,
            command=lambda: self._confirm_power_action("shutdown")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        ctk.CTkButton(
            power_btn_box,
            text="Reiniciar Remotamente",
            image=get_icon("refresh", TEXT_SECONDARY, 14),
            compound="left",
            font=FONTS["body_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            height=32,
            corner_radius=UI_RADIUS,
            command=lambda: self._confirm_power_action("reboot")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))

    def _start_service_scan(self) -> None:
        ip = self.machine.get("ip")
        if not ip:
            return

        def _worker():
            results = SystemService.check_machine_services(ip)
            try:
                if self.winfo_exists():
                    self.after(0, lambda: self._apply_service_results(results))
            except (tk.TclError, RuntimeError):
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_service_results(self, results: Dict[str, bool]) -> None:
        if not self.winfo_exists():
            return
        for srv, is_open in results.items():
            lbl = self._service_labels.get(srv)
            if not lbl:
                continue
            if is_open:
                lbl.configure(
                    text="  ACTIVO",
                    image=get_status_dot(ACCENT_EMERALD, 6),
                    text_color=ACCENT_EMERALD,
                    fg_color=BG_ROW
                )
            else:
                lbl.configure(
                    text="  SIN RESPUESTA",
                    image=get_status_dot(TEXT_DISABLED, 6),
                    text_color=TEXT_DISABLED,
                    fg_color=BG_ROW
                )

    def _launch_rdp(self) -> None:
        ip = self.machine.get("ip")
        ok, msg = SystemService.launch_rdp(ip)
        self.audit.log("RDP_LAUNCH", host=self.machine.get("name"), ip=ip, mac=self.machine.get("mac"), status="SUCCESS" if ok else "ERROR", details=msg)
        if not ok:
            messagebox.showerror("Error RDP", msg)

    def _launch_ssh(self) -> None:
        ip = self.machine.get("ip")
        ok, msg = SystemService.launch_ssh(ip)
        self.audit.log("SSH_LAUNCH", host=self.machine.get("name"), ip=ip, mac=self.machine.get("mac"), status="SUCCESS" if ok else "ERROR", details=msg)
        if not ok:
            messagebox.showerror("Error SSH", msg)

    def _confirm_power_action(self, action: str) -> None:
        name = self.machine.get("name", "el equipo")
        ip = self.machine.get("ip")
        act_title = "Reinicio" if action == "reboot" else "Apagado"
        confirm = messagebox.askyesno(
            f"Confirmar {act_title} Remoto",
            f"¿Estás seguro de que deseas ordenar el {act_title.lower()} de '{name}' ({ip})?\n\n"
            "El sistema operativo remoto iniciará una cuenta atrás de 30 segundos permitiendo cerrar tareas.",
            icon="warning"
        )
        if not confirm:
            return

        ok, msg = SystemService.remote_power_action(ip, action=action, timeout_sec=30)
        self.audit.log(
            f"REMOTE_{action.upper()}",
            host=name,
            ip=ip,
            mac=self.machine.get("mac"),
            status="SUCCESS" if ok else "ERROR",
            details=msg
        )
        if ok:
            messagebox.showinfo(f"{act_title} Ordenado", msg)
        else:
            messagebox.showerror("Error de Comunicación", msg)
