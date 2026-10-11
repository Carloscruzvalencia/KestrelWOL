"""
Componente Tarjeta de Dispositivo (ui/components/device_card.py)
KestrelWOL - CustomTkinter
"""

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Dict, Optional
import customtkinter as ctk

from core.config import (
    ACCENT_AMBER,
    ACCENT_BLUE,
    ACCENT_EMERALD,
    ACCENT_ROSE,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_INPUT,
    FONTS,
    HOVER_BLUE,
    HOVER_EMERALD,
    HOVER_ROSE,
    HOVER_SECONDARY,
    STATUS_COLORS,
    TEXT_MUTED,
    TEXT_PRIMARY,
)
from services.audit_service import AuditService
from services.system_service import SystemService
from ui.components.computer_icon import ComputerIconComponent


class DeviceCardComponent(ctk.CTkFrame):
    """
    Tarjeta individual de puesto:
    - Estado de monitor interactivo en tiempo real.
    - Diagnóstico de servicios (RDP y SSH) integrado dentro de la caja de red.
    - Distribución en 2 filas equilibradas con autoexpansión horizontal (0% recortes):
        * Fila Energía: [⚡ Encender] [🛑 Apagar] [🔄 Reiniciar]
        * Fila Acceso:  [🖥️ RDP] [💻 SSH] [⏰ Horario] [✏️] [❌]
    """

    def __init__(
        self,
        parent,
        machine: Dict[str, Any],
        on_wake: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_edit: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_delete: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_schedule: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_remote_control: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_launch_rdp: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_launch_ssh: Optional[Callable[[Dict[str, Any]], None]] = None,
        show_network_info: bool = False,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=BG_CARD,
            border_color=BG_INPUT,
            border_width=1,
            corner_radius=8,
            **kwargs
        )

        self.machine = machine
        self.on_wake = on_wake
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_schedule = on_schedule
        self.on_remote_control = on_remote_control
        self.on_launch_rdp = on_launch_rdp
        self.on_launch_ssh = on_launch_ssh
        self._show_network_info = show_network_info

        self.audit = AuditService()
        self._build_ui()
        self._start_diag_check()

    def _build_ui(self) -> None:

        # ======================================================================
        # 1. CABECERA: Nombre + Zona + Estado + Botones discretos (Editar / Borrar)
        # ======================================================================
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill=tk.X, padx=12, pady=(10, 6))

        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.pack(side=tk.LEFT, fill=tk.Y)

        lbl_name = ctk.CTkLabel(
            left_header,
            text=self.machine.get("name", "Unknown"),
            font=FONTS["title_card"],
            text_color=TEXT_PRIMARY
        )
        lbl_name.pack(side=tk.LEFT)

        zone_name = self.machine.get("zone", "General")
        btn_zone = ctk.CTkButton(
            left_header,
            text=f"📍 {zone_name}",
            font=FONTS["caption_bold"],
            fg_color="#082f49",
            hover_color="#0369a1",
            text_color="#38bdf8",
            height=20,
            corner_radius=4,
            command=lambda: self.on_edit(self.machine) if self.on_edit else None
        )
        btn_zone.pack(side=tk.LEFT, padx=(6, 0))

        self.lbl_status = ctk.CTkLabel(
            left_header,
            text="● Comprobando...",
            font=FONTS["caption_bold"],
            text_color=TEXT_MUTED,
            fg_color=BG_CONTAINER_DARK,
            corner_radius=4,
            padx=6,
            pady=2
        )
        self.lbl_status.pack(side=tk.LEFT, padx=(6, 0))

        # ======================================================================
        # 2. CUERPO: Icono + IP/MAC Ocultables + DIAGNÓSTICO EN VIVO
        # ======================================================================
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.comp_icon = ComputerIconComponent(body_frame, size=(48, 42), bg_color=BG_CARD)
        self.comp_icon.pack(side=tk.LEFT, padx=(0, 8))

        info_box = ctk.CTkFrame(body_frame, fg_color=BG_CONTAINER_DARK, corner_radius=6)
        info_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Columna A: IP y MAC (ocultas por defecto, clicables para alternar)
        text_subframe = ctk.CTkFrame(info_box, fg_color="transparent")
        text_subframe.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=4)

        self.lbl_ip = ctk.CTkLabel(
            text_subframe,
            text="",
            font=FONTS["mono_data"],
            text_color=TEXT_PRIMARY,
            anchor="w",
            cursor="hand2"
        )
        self.lbl_ip.pack(fill=tk.X)
        self.lbl_ip.bind("<Button-1>", lambda e: self.toggle_network_visibility())

        self.lbl_mac = ctk.CTkLabel(
            text_subframe,
            text="",
            font=FONTS["mono_data"],
            text_color=TEXT_MUTED,
            anchor="w",
            cursor="hand2"
        )
        self.lbl_mac.pack(fill=tk.X)
        self.lbl_mac.bind("<Button-1>", lambda e: self.toggle_network_visibility())

        # Botón Toggle Privacidad (Ver / Ocultar IP y MAC)
        self.btn_toggle_network = ctk.CTkButton(
            info_box,
            text="👁️",
            width=28,
            height=28,
            font=FONTS["caption_bold"],
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#94a3b8",
            corner_radius=4,
            command=self.toggle_network_visibility
        )
        self.btn_toggle_network.pack(side=tk.LEFT, padx=(2, 6), pady=4)

        self._update_network_display()

        # Columna B: Diagnóstico de Servicios de Red (En el espacio negro)
        diag_subframe = ctk.CTkFrame(info_box, fg_color="transparent")
        diag_subframe.pack(side=tk.RIGHT, padx=8, pady=4)

        self.lbl_rdp_diag = ctk.CTkLabel(
            diag_subframe,
            text="RDP: ⏳",
            font=FONTS["caption_bold"],
            text_color=TEXT_MUTED,
            fg_color="#1e293b",
            corner_radius=4,
            padx=6,
            pady=2
        )
        self.lbl_rdp_diag.pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_ssh_diag = ctk.CTkLabel(
            diag_subframe,
            text="SSH: ⏳",
            font=FONTS["caption_bold"],
            text_color=TEXT_MUTED,
            fg_color="#1e293b",
            corner_radius=4,
            padx=6,
            pady=2
        )
        self.lbl_ssh_diag.pack(side=tk.LEFT)

        # ======================================================================
        # 3. BARRA HORARIO PROGRAMADO
        # ======================================================================
        sched_bar = ctk.CTkFrame(self, fg_color="transparent")
        sched_bar.pack(fill=tk.X, padx=12, pady=(0, 6))

        sched_text, sched_color = self._format_schedule_text()
        has_sched = bool(self.machine.get("schedule", {}).get("enabled"))
        self.lbl_sched = ctk.CTkLabel(
            sched_bar,
            text=sched_text,
            font=FONTS["caption_bold"],
            text_color=sched_color,
            fg_color="#1e293b" if has_sched else BG_CONTAINER_DARK,
            corner_radius=4,
            padx=8,
            pady=2,
            anchor="w"
        )
        self.lbl_sched.pack(side=tk.LEFT)

        # ======================================================================
        # 4. FILA 1 DE BOTONES: CONTROL DE ENERGÍA (ENCENDER / APAGAR / REINICIAR)
        # ======================================================================
        row_power = ctk.CTkFrame(self, fg_color="transparent")
        row_power.pack(fill=tk.X, padx=12, pady=(0, 4))

        # Encender
        self.btn_wake = ctk.CTkButton(
            row_power,
            text="⚡ Encender",
            height=28,
            font=FONTS["body_bold"],
            fg_color=ACCENT_EMERALD,
            hover_color=HOVER_EMERALD,
            text_color=TEXT_PRIMARY,
            command=lambda: self.on_wake(self.machine) if self.on_wake else None
        )
        self.btn_wake.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        # Apagar
        ctk.CTkButton(
            row_power,
            text="🛑 Apagar",
            height=28,
            font=FONTS["caption_bold"],
            fg_color=ACCENT_ROSE,
            hover_color=HOVER_ROSE,
            text_color=TEXT_PRIMARY,
            command=self._handle_shutdown
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Reiniciar
        ctk.CTkButton(
            row_power,
            text="🔄 Reiniciar",
            height=28,
            font=FONTS["caption_bold"],
            fg_color="#b45309",
            hover_color="#d97706",
            text_color=TEXT_PRIMARY,
            command=self._handle_reboot
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        # ======================================================================
        # 5. FILA 2 DE BOTONES: ACCESO REMOTO Y HERRAMIENTAS (RDP / SSH / HORARIO)
        # ======================================================================
        row_tools = ctk.CTkFrame(self, fg_color="transparent")
        row_tools.pack(fill=tk.X, padx=12, pady=(0, 10))

        # RDP
        ctk.CTkButton(
            row_tools,
            text="🖥️ RDP",
            height=28,
            font=FONTS["caption_bold"],
            fg_color="#0284c7",
            hover_color="#0369a1",
            text_color=TEXT_PRIMARY,
            command=self._handle_rdp
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        # SSH
        ctk.CTkButton(
            row_tools,
            text="💻 SSH",
            height=28,
            font=FONTS["caption_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            command=self._handle_ssh
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Programador (más legible)
        ctk.CTkButton(
            row_tools,
            text="⏰ Horario",
            height=28,
            font=FONTS["caption_bold"],
            fg_color=ACCENT_AMBER if has_sched else BG_INPUT,
            hover_color="#d97706" if has_sched else HOVER_SECONDARY,
            text_color="#0f172a" if has_sched else TEXT_PRIMARY,
            command=lambda: self.on_schedule(self.machine) if self.on_schedule else None
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Editar dispositivo (botón estilizado con hover Slate)
        ctk.CTkButton(
            row_tools,
            text="✏️",
            width=30,
            height=28,
            font=FONTS["body_bold"],
            fg_color=BG_INPUT,
            hover_color=HOVER_SECONDARY,
            text_color=TEXT_PRIMARY,
            command=lambda: self.on_edit(self.machine) if self.on_edit else None
        ).pack(side=tk.LEFT, padx=2)

        # Eliminar dispositivo (botón estilizado con hover Rose)
        ctk.CTkButton(
            row_tools,
            text="❌",
            width=30,
            height=28,
            font=FONTS["body_bold"],
            fg_color=BG_INPUT,
            hover_color=ACCENT_ROSE,
            text_color=TEXT_PRIMARY,
            command=lambda: self.on_delete(self.machine) if self.on_delete else None
        ).pack(side=tk.LEFT, padx=(2, 0))

    # ==========================================================================
    # LÓGICA DE CONTROL, TELEMETRÍA Y ACCIONES
    # ==========================================================================
    def _format_schedule_text(self) -> tuple[str, str]:
        schedule = self.machine.get("schedule")
        if not schedule or not schedule.get("enabled") or not schedule.get("time"):
            return "🕒 Sin programar", TEXT_MUTED

        days = schedule.get("days", [])
        day_names = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        if len(days) == 7:
            d_str = "Diario"
        elif set(days) == {0, 1, 2, 3, 4}:
            d_str = "Lun-Vie"
        elif set(days) == {5, 6}:
            d_str = "Fines de sem."
        elif days:
            d_str = ", ".join([day_names[d] for d in sorted(days) if 0 <= d < 7])
        else:
            d_str = "Ninguno"

        return f"⏰ {schedule['time']} ({d_str})", ACCENT_AMBER

    def _start_diag_check(self) -> None:
        """Escanea en segundo plano si los puertos RDP y SSH responden."""
        ip = self.machine.get("ip")
        if not ip:
            return

        def _worker():
            res = SystemService.check_machine_services(ip)
            if self.winfo_exists():
                self.after(0, lambda: self._apply_diag_results(res))

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_diag_results(self, res: Dict[str, bool]) -> None:
        if not self.winfo_exists():
            return
        if res.get("rdp"):
            self.lbl_rdp_diag.configure(text="RDP: ● Activo", fg_color="#064e3b", text_color="#34d399")
        else:
            self.lbl_rdp_diag.configure(text="RDP: ○ Inactivo", fg_color="#1e293b", text_color="#64748b")

        if res.get("ssh"):
            self.lbl_ssh_diag.configure(text="SSH: ● Activo", fg_color="#064e3b", text_color="#34d399")
        else:
            self.lbl_ssh_diag.configure(text="SSH: ○ Inactivo", fg_color="#1e293b", text_color="#64748b")

    def update_status(self, status: str) -> None:
        """Actualiza el estado gráfico de forma thread-safe."""
        cfg = STATUS_COLORS.get(status, STATUS_COLORS["pending"])
        self.comp_icon.set_state(status)
        self.lbl_status.configure(
            text=cfg["text"],
            fg_color=cfg["bg"],
            text_color=cfg["fg"]
        )
        if status == "online":
            self._start_diag_check()
        elif status == "offline":
            self.lbl_rdp_diag.configure(text="RDP: ○ Inactivo", fg_color="#1e293b", text_color="#64748b")
            self.lbl_ssh_diag.configure(text="SSH: ○ Inactivo", fg_color="#1e293b", text_color="#64748b")

    def _handle_rdp(self) -> None:
        if self.on_launch_rdp:
            self.on_launch_rdp(self.machine)
        else:
            ip = self.machine.get("ip")
            SystemService.launch_rdp(ip)

    def _handle_ssh(self) -> None:
        if self.on_launch_ssh:
            self.on_launch_ssh(self.machine)
        else:
            ip = self.machine.get("ip")
            SystemService.launch_ssh(ip)

    def _handle_shutdown(self) -> None:
        name = self.machine.get("name", "el equipo")
        ip = self.machine.get("ip")
        if not ip:
            messagebox.showwarning("Aviso", "El equipo no tiene una IP configurada.")
            return

        if not messagebox.askyesno(
            "Confirmar Apagado Remoto",
            f"¿Deseas ordenar el APAGADO remoto de '{name}' ({ip})?\n\n"
            "El sistema remoto iniciará una cuenta atrás de 30 segundos permitiendo cerrar tareas.",
            icon="warning"
        ):
            return

        ok, msg = SystemService.remote_power_action(ip, action="shutdown", timeout_sec=30)
        self.audit.log(
            "REMOTE_SHUTDOWN",
            host=name,
            ip=ip,
            mac=self.machine.get("mac"),
            status="SUCCESS" if ok else "ERROR",
            details=msg
        )
        if ok:
            messagebox.showinfo("Apagado Ordenado", msg)
        else:
            messagebox.showerror("Error de Comunicación", msg)

    def _handle_reboot(self) -> None:
        name = self.machine.get("name", "el equipo")
        ip = self.machine.get("ip")
        if not ip:
            messagebox.showwarning("Aviso", "El equipo no tiene una IP configurada.")
            return

        if not messagebox.askyesno(
            "Confirmar Reinicio Remoto",
            f"¿Deseas ordenar el REINICIO remoto de '{name}' ({ip})?\n\n"
            "El sistema remoto reiniciará en 30 segundos tras avisar a los usuarios.",
            icon="warning"
        ):
            return

        ok, msg = SystemService.remote_power_action(ip, action="reboot", timeout_sec=30)
        self.audit.log(
            "REMOTE_REBOOT",
            host=name,
            ip=ip,
            mac=self.machine.get("mac"),
            status="SUCCESS" if ok else "ERROR",
            details=msg
        )
        if ok:
            messagebox.showinfo("Reinicio Ordenado", msg)
        else:
            messagebox.showerror("Error de Comunicación", msg)

    # --------------------------------------------------------------------------
    # PRIVACIDAD Y VISIBILIDAD DE RED (IP / MAC)
    # --------------------------------------------------------------------------
    def toggle_network_visibility(self) -> None:
        """Alterna la visibilidad de la IP y MAC en la tarjeta."""
        self._show_network_info = not self._show_network_info
        self._update_network_display()

    def set_network_visibility(self, visible: bool) -> None:
        """Establece explícitamente si mostrar u ocultar la IP y MAC."""
        self._show_network_info = visible
        self._update_network_display()

    def _update_network_display(self) -> None:
        """Renderiza los datos reales o enmascarados de IP y MAC."""
        raw_ip = self.machine.get("ip", "N/A")
        raw_mac = self.machine.get("mac", "N/A")

        if self._show_network_info:
            self.lbl_ip.configure(text=f"IP:   {raw_ip}")
            self.lbl_mac.configure(text=f"MAC:  {raw_mac}")
            self.btn_toggle_network.configure(
                text="🔒",
                fg_color="#334155",
                hover_color="#475569"
            )
        else:
            masked_ip = "●●●.●●●.●●●.●●●" if raw_ip != "N/A" else "N/A"
            masked_mac = "●●:●●:●●:●●:●●:●●" if raw_mac != "N/A" else "N/A"
            self.lbl_ip.configure(text=f"IP:   {masked_ip}")
            self.lbl_mac.configure(text=f"MAC:  {masked_mac}")
            self.btn_toggle_network.configure(
                text="👁️",
                fg_color="#1e293b",
                hover_color="#334155"
            )

