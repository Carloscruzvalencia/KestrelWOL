"""
Componente Tarjeta de Dispositivo (ui/components/device_card.py)
KestrelWOL - CustomTkinter (Industrial Enterprise Dark Mode)
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
    BG_BORDER,
    BG_BORDER_BUTTON,
    BG_BORDER_HOVER,
    BG_BTN_SECONDARY,
    BG_CARD,
    BG_CONTAINER_DARK,
    BG_ROW,
    FONTS,
    HOVER_SECONDARY,
    STATUS_COLORS,
    TEXT_DISABLED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    UI_RADIUS,
)
from services.audit_service import AuditService
from services.system_service import SystemService
from ui.components.computer_icon import ComputerIconComponent
from ui.components.icons import get_icon, get_status_dot


class DeviceCardComponent(ctk.CTkFrame):
    """
    Tarjeta individual de puesto (diseño cuadrado/modular preservado):
    - Superficie #111318 con borde hairline 1px (#222630 -> #2E3440 en hover).
    - Telemetría con punto circular de 6px y micro-etiquetas en mayúsculas.
    - Botones con width=0 para evitar recortes en anchos de 2 o 3 columnas.
    - Menú contextual oscuro (`...`) para Editar / Eliminar sin saturar la tarjeta.
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
            border_color=BG_BORDER,
            border_width=1,
            corner_radius=UI_RADIUS,
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
        self._bind_hover_border()
        self._start_diag_check()

    def _bind_hover_border(self) -> None:
        self.bind("<Enter>", lambda _e: self.configure(border_color=BG_BORDER_HOVER))
        self.bind("<Leave>", lambda _e: self.configure(border_color=BG_BORDER))

    def _build_ui(self) -> None:
        # ======================================================================
        # 1. CABECERA: Nombre + Etiqueta Zona compacta + Telemetría (punto 6px)
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
            text=zone_name,
            image=get_icon("tag", TEXT_MUTED, 11),
            compound="left",
            font=FONTS["caption_normal"],
            fg_color=BG_ROW,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER,
            text_color=TEXT_MUTED,
            width=0,
            height=22,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_edit(self.machine) if self.on_edit else None
        )
        btn_zone.pack(side=tk.LEFT, padx=(8, 0))

        self.lbl_status = ctk.CTkLabel(
            header_frame,
            text="  SONDEO",
            image=get_status_dot(ACCENT_BLUE, 6),
            compound="left",
            font=FONTS["micro"],
            text_color=TEXT_MUTED,
            fg_color="transparent",
            padx=4,
            pady=2
        )
        self.lbl_status.pack(side=tk.RIGHT)

        # ======================================================================
        # 2. CUERPO: Icono Vectorial + IP/MAC Monoespaciado + Diagnóstico
        # ======================================================================
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill=tk.X, padx=12, pady=(0, 6))

        self.comp_icon = ComputerIconComponent(body_frame, size=(46, 40), bg_color=BG_CARD)
        self.comp_icon.pack(side=tk.LEFT, padx=(0, 8))

        info_box = ctk.CTkFrame(
            body_frame,
            fg_color=BG_CONTAINER_DARK,
            border_width=1,
            border_color=BG_BORDER,
            corner_radius=UI_RADIUS
        )
        info_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Columna A: IP y MAC (ocultas por defecto, clicables para alternar)
        text_subframe = ctk.CTkFrame(info_box, fg_color="transparent")
        text_subframe.pack(side=tk.LEFT, fill=tk.Y, padx=(8, 4), pady=5)

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
            text="",
            image=get_icon("eye", TEXT_MUTED, 14),
            width=28,
            height=28,
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            corner_radius=UI_RADIUS,
            command=self.toggle_network_visibility
        )
        self.btn_toggle_network.pack(side=tk.LEFT, padx=(2, 6), pady=5)

        self._update_network_display()

        # Columna B: Diagnóstico de Servicios de Red (Apilados verticalmente para compactar ancho)
        diag_subframe = ctk.CTkFrame(info_box, fg_color="transparent")
        diag_subframe.pack(side=tk.RIGHT, padx=8, pady=4)

        self.lbl_rdp_diag = ctk.CTkLabel(
            diag_subframe,
            text="  RDP",
            image=get_status_dot(TEXT_DISABLED, 6),
            compound="left",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED,
            fg_color=BG_ROW,
            corner_radius=UI_RADIUS,
            padx=7,
            pady=1
        )
        self.lbl_rdp_diag.pack(anchor="e", pady=(0, 3))

        self.lbl_ssh_diag = ctk.CTkLabel(
            diag_subframe,
            text="  SSH",
            image=get_status_dot(TEXT_DISABLED, 6),
            compound="left",
            font=FONTS["micro"],
            text_color=TEXT_DISABLED,
            fg_color=BG_ROW,
            corner_radius=UI_RADIUS,
            padx=7,
            pady=1
        )
        self.lbl_ssh_diag.pack(anchor="e")

        # ======================================================================
        # 3. BARRA HORARIO PROGRAMADO (discreta)
        # ======================================================================
        sched_bar = ctk.CTkFrame(self, fg_color="transparent")
        sched_bar.pack(fill=tk.X, padx=12, pady=(0, 6))

        sched_text, sched_color = self._format_schedule_text()
        has_sched = bool(self.machine.get("schedule", {}).get("enabled"))
        self.lbl_sched = ctk.CTkLabel(
            sched_bar,
            text=f"  {sched_text}",
            image=get_icon("clock", ACCENT_AMBER if has_sched else TEXT_DISABLED, 12),
            compound="left",
            font=FONTS["caption_bold"] if has_sched else FONTS["caption_normal"],
            text_color=sched_color,
            fg_color=BG_ROW if has_sched else "transparent",
            corner_radius=UI_RADIUS,
            padx=8 if has_sched else 2,
            pady=2,
            anchor="w"
        )
        self.lbl_sched.pack(side=tk.LEFT)

        # ======================================================================
        # 4. FILA 1 DE BOTONES: CONTROL DE ENERGÍA (width=0 evita recortes)
        # ======================================================================
        row_power = ctk.CTkFrame(self, fg_color="transparent")
        row_power.pack(fill=tk.X, padx=12, pady=(0, 5))

        # Encender
        self.btn_wake = ctk.CTkButton(
            row_power,
            text="Encender",
            image=get_icon("power", ACCENT_EMERALD, 14),
            compound="left",
            width=0,
            height=30,
            font=FONTS["body_bold"],
            fg_color="#102820",
            hover_color="#16382D",
            border_width=1,
            border_color="#1D4D3D",
            text_color=ACCENT_EMERALD,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_wake(self.machine) if self.on_wake else None
        )
        self.btn_wake.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        # Apagar (Neutro hasta hover rojo destructivo #EF4444)
        ctk.CTkButton(
            row_power,
            text="Apagar",
            image=get_icon("power_off", TEXT_MUTED, 14),
            compound="left",
            width=0,
            height=30,
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=ACCENT_ROSE,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_MUTED,
            corner_radius=UI_RADIUS,
            command=self._handle_shutdown
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Reiniciar (Monocromo secundario)
        ctk.CTkButton(
            row_power,
            text="Reiniciar",
            image=get_icon("refresh", TEXT_SECONDARY, 14),
            compound="left",
            width=0,
            height=30,
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            corner_radius=UI_RADIUS,
            command=self._handle_reboot
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(4, 0))

        # ======================================================================
        # 5. FILA 2 DE BOTONES: ACCESO REMOTO + MENÚ CONTEXTUAL (...)
        # ======================================================================
        row_tools = ctk.CTkFrame(self, fg_color="transparent")
        row_tools.pack(fill=tk.X, padx=12, pady=(0, 10))

        # RDP
        ctk.CTkButton(
            row_tools,
            text="RDP",
            image=get_icon("monitor", TEXT_SECONDARY, 14),
            compound="left",
            width=0,
            height=30,
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            corner_radius=UI_RADIUS,
            command=self._handle_rdp
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        # SSH
        ctk.CTkButton(
            row_tools,
            text="SSH",
            image=get_icon("terminal", TEXT_SECONDARY, 14),
            compound="left",
            width=0,
            height=30,
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            text_color=TEXT_SECONDARY,
            corner_radius=UI_RADIUS,
            command=self._handle_ssh
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Programador
        ctk.CTkButton(
            row_tools,
            text="Horario",
            image=get_icon("clock", ACCENT_AMBER if has_sched else TEXT_SECONDARY, 14),
            compound="left",
            width=0,
            height=30,
            font=FONTS["caption_bold"],
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color="#3D3118" if has_sched else BG_BORDER_BUTTON,
            text_color=ACCENT_AMBER if has_sched else TEXT_SECONDARY,
            corner_radius=UI_RADIUS,
            command=lambda: self.on_schedule(self.machine) if self.on_schedule else None
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Botón de opciones contextuales (...) -> Editar / Eliminar (sin aplastar botones)
        self.btn_more = ctk.CTkButton(
            row_tools,
            text="",
            image=get_icon("more", TEXT_SECONDARY, 14),
            width=34,
            height=30,
            fg_color=BG_BTN_SECONDARY,
            hover_color=HOVER_SECONDARY,
            border_width=1,
            border_color=BG_BORDER_BUTTON,
            corner_radius=UI_RADIUS,
            command=self._show_context_menu
        )
        self.btn_more.pack(side=tk.LEFT, padx=(4, 0))

    def _show_context_menu(self) -> None:
        """Abre un menú contextual oscuro con las acciones de gestión de la tarjeta."""
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            activebackground=BG_ROW,
            activeforeground=ACCENT_EMERALD,
            bd=1,
            relief="solid",
            font=("Segoe UI", 9)
        )
        menu.add_command(
            label="  Editar dispositivo",
            command=lambda: self.on_edit(self.machine) if self.on_edit else None
        )
        menu.add_command(
            label="  Programar horario",
            command=lambda: self.on_schedule(self.machine) if self.on_schedule else None
        )
        menu.add_separator()
        menu.add_command(
            label="  Eliminar dispositivo",
            foreground=ACCENT_ROSE,
            activeforeground=ACCENT_ROSE,
            command=lambda: self.on_delete(self.machine) if self.on_delete else None
        )
        try:
            x = self.btn_more.winfo_rootx()
            y = self.btn_more.winfo_rooty() + self.btn_more.winfo_height()
            menu.tk_popup(x, y)
        except Exception:
            pass

    # ==========================================================================
    # LÓGICA DE CONTROL, TELEMETRÍA Y ACCIONES
    # ==========================================================================
    def _format_schedule_text(self) -> tuple[str, str]:
        schedule = self.machine.get("schedule")
        if not schedule or not schedule.get("enabled") or not schedule.get("time"):
            return "Sin programar", TEXT_DISABLED

        days = schedule.get("days", [])
        day_names = ["LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"]
        if len(days) == 7:
            d_str = "DIARIO"
        elif set(days) == {0, 1, 2, 3, 4}:
            d_str = "LUN-VIE"
        elif set(days) == {5, 6}:
            d_str = "FIN DE SEM."
        elif days:
            d_str = ", ".join([day_names[d] for d in sorted(days) if 0 <= d < 7])
        else:
            d_str = "NINGUNO"

        return f"{schedule['time']} ({d_str})", ACCENT_AMBER

    def _start_diag_check(self) -> None:
        """Escanea en segundo plano si los puertos RDP y SSH responden."""
        ip = self.machine.get("ip")
        if not ip:
            return

        def _worker():
            res = SystemService.check_machine_services(ip)
            try:
                if self.winfo_exists():
                    self.after(0, lambda: self._apply_diag_results(res))
            except (tk.TclError, RuntimeError):
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_diag_results(self, res: Dict[str, bool]) -> None:
        if not self.winfo_exists():
            return
        if res.get("rdp"):
            self.lbl_rdp_diag.configure(
                text="  RDP",
                image=get_status_dot(ACCENT_EMERALD, 6),
                fg_color=BG_ROW,
                text_color=ACCENT_EMERALD
            )
        else:
            self.lbl_rdp_diag.configure(
                text="  RDP",
                image=get_status_dot(TEXT_DISABLED, 6),
                fg_color=BG_ROW,
                text_color=TEXT_DISABLED
            )

        if res.get("ssh"):
            self.lbl_ssh_diag.configure(
                text="  SSH",
                image=get_status_dot(ACCENT_EMERALD, 6),
                fg_color=BG_ROW,
                text_color=ACCENT_EMERALD
            )
        else:
            self.lbl_ssh_diag.configure(
                text="  SSH",
                image=get_status_dot(TEXT_DISABLED, 6),
                fg_color=BG_ROW,
                text_color=TEXT_DISABLED
            )

    def update_status(self, status: str) -> None:
        """Actualiza el estado gráfico de forma thread-safe."""
        cfg = STATUS_COLORS.get(status, STATUS_COLORS["pending"])
        self.comp_icon.set_state(status)
        self.lbl_status.configure(
            text=f"  {cfg['text']}",
            image=get_status_dot(cfg["dot"], 6),
            fg_color="transparent",
            text_color=cfg["fg"]
        )
        if status == "online":
            self._start_diag_check()
        elif status == "offline":
            self.lbl_rdp_diag.configure(
                text="  RDP",
                image=get_status_dot(TEXT_DISABLED, 6),
                fg_color=BG_ROW,
                text_color=TEXT_DISABLED
            )
            self.lbl_ssh_diag.configure(
                text="  SSH",
                image=get_status_dot(TEXT_DISABLED, 6),
                fg_color=BG_ROW,
                text_color=TEXT_DISABLED
            )

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
            self.lbl_ip.configure(text=f"IP   {raw_ip}")
            self.lbl_mac.configure(text=f"MAC  {raw_mac}")
            self.btn_toggle_network.configure(
                image=get_icon("eye_off", TEXT_SECONDARY, 14),
                fg_color=BG_ROW,
                hover_color=HOVER_SECONDARY
            )
        else:
            masked_ip = "***.***.***.***" if raw_ip != "N/A" else "N/A"
            masked_mac = "**:**:**:**:**:**" if raw_mac != "N/A" else "N/A"
            self.lbl_ip.configure(text=f"IP   {masked_ip}")
            self.lbl_mac.configure(text=f"MAC  {masked_mac}")
            self.btn_toggle_network.configure(
                image=get_icon("eye", TEXT_MUTED, 14),
                fg_color=BG_BTN_SECONDARY,
                hover_color=HOVER_SECONDARY
            )
