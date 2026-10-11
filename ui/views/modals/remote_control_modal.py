"""
Modal de Control Remoto, Conexión Rápida y Diagnóstico de Servicios
(ui/views/modals/remote_control_modal.py)
KestrelWOL - CustomTkinter
"""

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_AMBER,
    ACCENT_BLUE,
    ACCENT_EMERALD,
    ACCENT_ROSE,
    ACCENT_SKY,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_DARK,
    BG_INPUT,
    FONTS,
    HOVER_BLUE,
    HOVER_EMERALD,
    HOVER_ROSE,
    HOVER_SECONDARY,
    MODAL_SIZES,
    TEXT_MUTED,
    TEXT_PRIMARY,
)
from services.audit_service import AuditService
from services.system_service import SystemService


class RemoteControlModal(ctk.CTkToplevel):
    """
    Diálogo para gestión remota del puesto:
    - Comprobación en vivo de servicios (RDP, SSH, VNC, HTTP/HTTPS).
    - Conexión rápida directa con un clic (RDP mstsc, consola SSH, visor Web).
    - Apagado y reinicio remoto controlado con aviso preventivo (Graceful Shutdown).
    """

    def __init__(self, parent, machine: Dict[str, Any], audit_service: Optional[AuditService] = None):
        super().__init__(parent)
        self.machine = machine
        self.audit = audit_service or AuditService()

        w, h = MODAL_SIZES.get("remote_control", (580, 530))
        self.title(f"⚡ Control y Conexión Remota - {machine.get('name', 'Puesto')}")
        self.geometry(f"{w}x{h}")
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

        # 1. Cabecera con info del equipo
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        header.pack(fill=tk.X, padx=16, pady=(16, 10))

        top_info = ctk.CTkFrame(header, fg_color="transparent")
        top_info.pack(fill=tk.X, padx=14, pady=10)

        ctk.CTkLabel(
            top_info,
            text=f"🖥️ {name}",
            font=FONTS["title_main"],
            text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        ctk.CTkLabel(
            top_info,
            text=f"📍 {zone}  |  IP: {ip}  |  MAC: {mac}",
            font=FONTS["caption_bold"],
            text_color=TEXT_MUTED
        ).pack(side=tk.RIGHT)

        # 2. Diagnóstico de Puertos y Servicios Remotos
        services_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        services_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            services_card,
            text="🔍 Diagnóstico de Servicios de Red",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=14, pady=(10, 6))

        grid_frame = ctk.CTkFrame(services_card, fg_color=BG_CONTAINER_DARK, corner_radius=6)
        grid_frame.pack(fill=tk.X, padx=14, pady=(0, 12))

        services_def = [
            ("rdp", "🖥️ RDP (Puerto 3389 - Escritorio Remoto)"),
            ("ssh", "💻 SSH (Puerto 22 - Consola Shell Segura)"),
        ]

        for idx, (srv_key, srv_label) in enumerate(services_def):
            row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            row_frame.pack(fill=tk.X, padx=10, pady=4)

            ctk.CTkLabel(
                row_frame,
                text=srv_label,
                font=FONTS["body_normal"],
                text_color=TEXT_PRIMARY
            ).pack(side=tk.LEFT)

            lbl_status = ctk.CTkLabel(
                row_frame,
                text="⏳ Comprobando...",
                font=FONTS["caption_bold"],
                text_color=TEXT_MUTED,
                fg_color=BG_INPUT,
                corner_radius=4,
                padx=8,
                pady=2
            )
            lbl_status.pack(side=tk.RIGHT)
            self._service_labels[srv_key] = lbl_status

        # 3. Conexión Rápida
        conn_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        conn_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            conn_card,
            text="🚀 Conexión Inmediata",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=14, pady=(10, 6))

        btn_conn_box = ctk.CTkFrame(conn_card, fg_color="transparent")
        btn_conn_box.pack(fill=tk.X, padx=14, pady=(0, 12))

        ctk.CTkButton(
            btn_conn_box,
            text="🖥️ Iniciar Sesión RDP",
            font=FONTS["body_bold"],
            fg_color=ACCENT_BLUE,
            hover_color=HOVER_BLUE,
            text_color=TEXT_PRIMARY,
            height=32,
            command=self._launch_rdp
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        ctk.CTkButton(
            btn_conn_box,
            text="💻 Abrir Consola SSH",
            font=FONTS["body_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            height=32,
            command=self._launch_ssh
        ).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 4. Gestión de Energía (Graceful Shutdown)
        power_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        power_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        ctk.CTkLabel(
            power_card,
            text="🛑 Control de Energía Remoto (Apagado / Reinicio)",
            font=FONTS["title_section"],
            text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=14, pady=(10, 6))

        power_btn_box = ctk.CTkFrame(power_card, fg_color="transparent")
        power_btn_box.pack(fill=tk.X, padx=14, pady=(0, 12))

        ctk.CTkButton(
            power_btn_box,
            text="🛑 Apagar Remotamente (30s)",
            font=FONTS["body_bold"],
            fg_color=ACCENT_ROSE,
            hover_color=HOVER_ROSE,
            text_color=TEXT_PRIMARY,
            height=32,
            command=lambda: self._confirm_power_action("shutdown")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        ctk.CTkButton(
            power_btn_box,
            text="🔄 Reiniciar Remotamente",
            font=FONTS["body_bold"],
            fg_color=ACCENT_AMBER,
            hover_color="#d97706",
            text_color="#0f172a",
            height=32,
            command=lambda: self._confirm_power_action("reboot")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))

    def _start_service_scan(self) -> None:
        ip = self.machine.get("ip")
        if not ip:
            return

        def _worker():
            results = SystemService.check_machine_services(ip)
            self.after(0, lambda: self._apply_service_results(results))

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_service_results(self, results: Dict[str, bool]) -> None:
        if not self.winfo_exists():
            return
        for srv, is_open in results.items():
            lbl = self._service_labels.get(srv)
            if not lbl:
                continue
            if is_open:
                lbl.configure(text="● Activo (Abierto)", text_color=ACCENT_EMERALD, fg_color="#064e3b")
            else:
                lbl.configure(text="○ No responde", text_color=TEXT_MUTED, fg_color=BG_INPUT)

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
