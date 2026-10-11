"""
Orquestador Principal de la Aplicación (ui/app.py)
KestrelWOL - CustomTkinter
"""

from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from core.config import (
    APP_TITLE,
    BASE_DIR,
    BG_DARK,
    WINDOW_DEFAULT_SIZE,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from core.events import safe_gui_dispatch
from services import (
    AuditService,
    MonitorService,
    ScannerService,
    SchedulerService,
    StorageService,
    SystemService,
    TrayService,
    WolService,
)
from ui.views import (
    DeviceAddView,
    DeviceGridView,
    HeaderView,
    SafetyFooterView,
    ZoneToolbarView,
)
from ui.views.modals import (
    AuditViewerModal,
    DeviceEditModal,
    IgnoredModal,
    LegalTermsModal,
    RemoteControlModal,
    SafetyConfirmModal,
    ScannerModal,
    ScheduleModal,
)


class WakeOnLanApp(ctk.CTk):
    """
    Ventana principal y orquestador del sistema:
    - Instancia e inyecta los servicios desacoplados.
    - Conecta las vistas mediante inversión de control (callbacks).
    - Despacha eventos multihilo hacia el Main Thread de forma segura.
    - Gestiona el ciclo de vida de los workers en segundo plano.
    """

    def __init__(self):
        super().__init__()

        # Configuración nativa de CustomTkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_TITLE)
        self.geometry(WINDOW_DEFAULT_SIZE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=BG_DARK)

        # 1. Inyección de Servicios
        self.storage_service = StorageService()
        self.audit_service = AuditService()
        self.wol_service = WolService(audit_service=self.audit_service)
        self.scanner_service = ScannerService(storage_service=self.storage_service)
        self.tray_service = TrayService(
            on_restore=self.bring_to_front,
            on_quit=self.on_close,
            app_title=APP_TITLE
        )

        # 2. Estado Operativo
        self.machines: List[Dict[str, Any]] = []
        self.selected_zone: str = "Todos"

        # 3. Construcción del Layout y Vistas
        self._build_layout()

        # 4. Inicialización de Workers en Segundo Plano
        self._init_services()

        # 5. Protocolo de cierre (minimiza a la bandeja para mantener el programador activo)
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def _build_layout(self) -> None:
        # A. Cabecera Superior
        self.header_view = HeaderView(
            self,
            on_open_terms=self.open_legal_terms,
            on_open_audit=self.open_audit_viewer,
            on_wake_all=self.handle_wake_all,
            on_import_csv=self.handle_import_csv,
            on_export_csv=self.handle_export_csv
        )
        self.header_view.pack(fill=tk.X, padx=16, pady=(12, 6))

        # B. Formulario de Alta
        self.device_add_view = DeviceAddView(
            self,
            get_zones_callback=self.storage_service.get_existing_zones,
            on_add_device=self.handle_add_device,
            on_open_scanner=self.open_network_scanner
        )
        self.device_add_view.pack(fill=tk.X, padx=16, pady=(0, 6))

        # C. Barra de Presets de Zonas
        self.zone_toolbar_view = ZoneToolbarView(
            self,
            on_zone_selected=self.handle_zone_selected,
            on_wake_zone=self.handle_wake_zone,
            on_toggle_network=self.handle_toggle_network
        )
        self.zone_toolbar_view.pack(fill=tk.X, padx=16, pady=(0, 6))

        # D. Banner Inferior Permanente (EULA)
        self.safety_footer_view = SafetyFooterView(
            self,
            on_open_terms=self.open_legal_terms
        )
        self.safety_footer_view.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(0, 8))

        # E. Cuadrícula Scrollable de Dispositivos (Centro)
        self.device_grid_view = DeviceGridView(
            self,
            on_wake_device=self.handle_wake_device,
            on_edit_device=self.handle_edit_device,
            on_delete_device=self.handle_delete_device,
            on_schedule_device=self.handle_schedule_device,
            on_remote_control_device=self.handle_remote_control_device,
            on_launch_rdp=self.handle_launch_rdp,
            on_launch_ssh=self.handle_launch_ssh
        )
        self.device_grid_view.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=16, pady=(0, 6))

    def _init_services(self) -> None:
        # Cargar máquinas iniciales
        self.machines = self.storage_service.load_machines()
        self.refresh_ui()

        # Comprobación de Privilegios de Admin
        if SystemService.is_admin():
            self.audit_service.log(
                "STARTUP",
                status="WARNING",
                details="App iniciada con privilegios de Administrador (se recomienda usuario estándar)"
            )
        else:
            self.audit_service.log(
                "STARTUP",
                status="SUCCESS",
                details="App iniciada en espacio de usuario estándar (mínimo privilegio)"
            )

        # Comprobación de Primer Inicio (Términos)
        if not self.storage_service.is_terms_accepted():
            self.after(150, lambda: LegalTermsModal(self, is_first_run=True, on_accept=self._on_terms_accepted))

        # Configurar y arrancar Monitor Worker
        self.monitor_service = MonitorService(on_status_change=self._on_monitor_status_change)
        self.monitor_service.set_machines(self.machines)
        self.monitor_service.start()

        # Configurar y arrancar Scheduler Worker
        self.scheduler_service = SchedulerService(
            on_trigger_wake=self.handle_wake_device,
            audit_service=self.audit_service
        )
        self.scheduler_service.set_machines(self.machines)
        self.scheduler_service.start()

    # --------------------------------------------------------------------------
    # GESTIÓN Y REFRESCADO DE LA INTERFAZ
    # --------------------------------------------------------------------------
    def refresh_ui(self) -> None:
        """Sincroniza todas las vistas con los datos actuales."""
        # 1. Contabilizar zonas con normalización canónica
        zone_counts: Dict[str, int] = {"Todos": len(self.machines)}
        for m in self.machines:
            c_zone = self.storage_service.canonicalize_zone(m.get("zone", "General"), self.machines)
            m["zone"] = c_zone
            zone_counts[c_zone] = zone_counts.get(c_zone, 0) + 1

        all_zones = ["Todos"] + sorted([k for k in zone_counts if k != "Todos"], key=lambda s: s.lower())

        # Validar selección actual
        if not any(z.lower() == self.selected_zone.lower() for z in all_zones):
            self.selected_zone = "Todos"

        # 2. Actualizar Barra de Presets
        self.zone_toolbar_view.render_zones(all_zones, zone_counts, self.selected_zone)

        # 3. Filtrar y Renderizar Tarjetas
        displayed = [
            m for m in self.machines
            if self.selected_zone == "Todos" or m.get("zone", "").lower() == self.selected_zone.lower()
        ]
        self.device_grid_view.render_devices(displayed)

        # 4. Sincronizar listas en los workers
        if hasattr(self, "monitor_service"):
            self.monitor_service.set_machines(self.machines)
        if hasattr(self, "scheduler_service"):
            self.scheduler_service.set_machines(self.machines)

    # --------------------------------------------------------------------------
    # EVENTOS DE USUARIO (ACTIONS)
    # --------------------------------------------------------------------------
    def handle_zone_selected(self, zone_name: str) -> None:
        self.selected_zone = zone_name
        self.refresh_ui()

    def handle_add_device(self, device_data: Dict[str, str]) -> None:
        name = device_data["name"]
        ip = device_data["ip"]
        mac = device_data["mac"]
        raw_zone = device_data["zone"]

        if not name or not ip or not mac:
            messagebox.showwarning("Datos Incompletos", "Por favor completa Nombre, IP y MAC.", parent=self)
            return

        if not WolService.validate_ip(ip):
            messagebox.showerror("IP Inválida", f"La dirección IP '{ip}' no cumple con el formato IPv4 estándar.", parent=self)
            return

        if not WolService.validate_mac(mac):
            messagebox.showerror("MAC Inválida", f"La dirección MAC '{mac}' no tiene un formato válido.", parent=self)
            return

        canonical_zone = self.storage_service.canonicalize_zone(raw_zone, self.machines)
        new_device = {
            "name": name,
            "ip": ip,
            "mac": mac,
            "zone": canonical_zone
        }

        self.machines.append(new_device)
        self.storage_service.save_machines(self.machines)
        self.audit_service.log(
            "DEVICE_ADDED",
            target_name=name,
            ip=ip,
            mac=mac,
            status="SUCCESS",
            details=f"Zona: '{canonical_zone}'"
        )

        self.device_add_view.clear(keep_zone=canonical_zone)
        self.refresh_ui()

    def handle_wake_device(self, machine: Dict[str, Any]) -> None:
        self.wol_service.wake_single(machine)

    def handle_wake_all(self) -> None:
        if not self.machines:
            messagebox.showinfo("Wake on LAN", "No hay dispositivos registrados en el panel.", parent=self)
            return

        SafetyConfirmModal(
            self,
            targets=list(self.machines),
            scope_title=f"todos los equipos ({len(self.machines)})",
            on_confirm=self._execute_staggered_wake
        )

    def handle_wake_zone(self, zone_name: str) -> None:
        if zone_name == "Todos":
            targets = list(self.machines)
        else:
            targets = [m for m in self.machines if m.get("zone", "").lower() == zone_name.lower()]

        if not targets:
            messagebox.showinfo("Wake on LAN", "No hay dispositivos en esta selección.", parent=self)
            return

        SafetyConfirmModal(
            self,
            targets=targets,
            scope_title=f"los equipos de '{zone_name}' ({len(targets)})",
            on_confirm=self._execute_staggered_wake
        )

    def _execute_staggered_wake(self, targets: List[Dict[str, Any]]) -> None:
        self.wol_service.wake_staggered_async(targets=targets)

    def handle_edit_device(self, machine: Dict[str, Any]) -> None:
        idx = next((i for i, m in enumerate(self.machines) if m is machine), -1)
        if idx == -1:
            return

        def on_saved(updated_machine: Dict[str, Any]):
            updated_machine["zone"] = self.storage_service.canonicalize_zone(updated_machine["zone"], self.machines)
            self.machines[idx] = updated_machine
            self.storage_service.save_machines(self.machines)
            self.audit_service.log(
                "DEVICE_EDITED",
                target_name=updated_machine["name"],
                ip=updated_machine["ip"],
                mac=updated_machine["mac"],
                status="SUCCESS",
                details=f"Zona: '{updated_machine['zone']}'"
            )
            self.refresh_ui()

        DeviceEditModal(
            self,
            machine=machine,
            get_zones_callback=self.storage_service.get_existing_zones,
            on_save=on_saved
        )

    def handle_delete_device(self, machine: Dict[str, Any]) -> None:
        if messagebox.askyesno("Confirmar Eliminación", f"¿Eliminar el equipo '{machine.get('name')}'?", parent=self):
            self.audit_service.log(
                "DEVICE_DELETED",
                target_name=machine.get("name"),
                ip=machine.get("ip"),
                mac=machine.get("mac"),
                status="SUCCESS"
            )
            self.machines = [m for m in self.machines if m is not machine]
            self.storage_service.save_machines(self.machines)
            self.refresh_ui()

    def handle_schedule_device(self, machine: Dict[str, Any]) -> None:
        idx = next((i for i, m in enumerate(self.machines) if m is machine), -1)
        if idx == -1:
            return

        def on_saved(sched: Dict[str, Any]):
            self.machines[idx]["schedule"] = sched
            self.storage_service.save_machines(self.machines)
            self.refresh_ui()

        ScheduleModal(self, machine=machine, on_save_schedule=on_saved)

    # --------------------------------------------------------------------------
    # MODALES GENERALES
    # --------------------------------------------------------------------------
    def open_legal_terms(self) -> None:
        LegalTermsModal(self, is_first_run=False)

    def open_audit_viewer(self) -> None:
        AuditViewerModal(self, audit_service=self.audit_service)

    def open_network_scanner(self) -> None:
        ScannerModal(
            self,
            scanner_service=self.scanner_service,
            storage_service=self.storage_service,
            on_select_device=self.device_add_view.populate_from_scan,
            on_open_ignored=lambda: IgnoredModal(self, storage_service=self.storage_service)
        )

    def handle_remote_control_device(self, machine: Dict[str, Any]) -> None:
        RemoteControlModal(self, machine=machine, audit_service=self.audit_service)

    def handle_launch_rdp(self, machine: Dict[str, Any]) -> None:
        ip = machine.get("ip")
        if not ip:
            messagebox.showwarning("Aviso RDP", "El equipo no tiene una dirección IP asignada.")
            return
        ok, msg = SystemService.launch_rdp(ip)
        self.audit_service.log(
            "RDP_LAUNCH",
            host=machine.get("name"),
            ip=ip,
            mac=machine.get("mac"),
            status="SUCCESS" if ok else "ERROR",
            details=msg
        )
        if not ok:
            messagebox.showerror("Error RDP", msg)

    def handle_launch_ssh(self, machine: Dict[str, Any]) -> None:
        ip = machine.get("ip")
        if not ip:
            messagebox.showwarning("Aviso SSH", "El equipo no tiene una dirección IP asignada.")
            return
        ok, msg = SystemService.launch_ssh(ip)
        self.audit_service.log(
            "SSH_LAUNCH",
            host=machine.get("name"),
            ip=ip,
            mac=machine.get("mac"),
            status="SUCCESS" if ok else "ERROR",
            details=msg
        )
        if not ok:
            messagebox.showerror("Error SSH", msg)

    def handle_import_csv(self) -> None:
        filepath_str = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de inventario",
            filetypes=[("Archivos CSV (*.csv)", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not filepath_str:
            return
        added, updated, msg = self.storage_service.import_machines_from_csv(Path(filepath_str))
        self.audit_service.log(
            "CSV_IMPORT",
            status="SUCCESS" if (added > 0 or updated > 0) else "WARNING",
            details=f"{msg} (Archivo: {Path(filepath_str).name})"
        )
        if added > 0 or updated > 0:
            self.machines = self.storage_service.load_machines()
            if hasattr(self, "monitor_service"):
                self.monitor_service.set_machines(self.machines)
            if hasattr(self, "scheduler_service"):
                self.scheduler_service.set_machines(self.machines)
            self.refresh_ui()
            messagebox.showinfo("Importación Exitosa", msg)
        else:
            messagebox.showwarning("Aviso de Importación", msg)

    def handle_export_csv(self) -> None:
        filepath_str = filedialog.asksaveasfilename(
            title="Guardar inventario como CSV",
            defaultextension=".csv",
            initialfile="equipos_wol_export.csv",
            filetypes=[("Archivos CSV (*.csv)", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not filepath_str:
            return
        ok, msg = self.storage_service.export_machines_to_csv(Path(filepath_str))
        self.audit_service.log(
            "CSV_EXPORT",
            status="SUCCESS" if ok else "ERROR",
            details=f"{msg} (Archivo: {Path(filepath_str).name})"
        )
        if ok:
            messagebox.showinfo("Exportación Exitosa", msg)
        else:
            messagebox.showerror("Error al Exportar", msg)

    def handle_toggle_network(self) -> bool:
        """Alterna la visualización de IPs y MACs en toda la cuadrícula de dispositivos."""
        return self.device_grid_view.toggle_all_network_visibility()

    def _on_terms_accepted(self) -> None:
        user = SystemService.is_admin() and "admin" or "operator"
        self.storage_service.save_terms_accepted(operator_user=user)
        self.audit_service.log("TERMS_ACCEPTED", status="SUCCESS")

    # --------------------------------------------------------------------------
    # DESPACHO DE WORKERS (THREAD-SAFE)
    # --------------------------------------------------------------------------
    def _on_monitor_status_change(self, machine: Dict[str, Any], status: str) -> None:
        safe_gui_dispatch(
            self,
            self.device_grid_view.update_device_status,
            machine.get("ip"),
            machine.get("mac"),
            status
        )

    def bring_to_front(self) -> None:
        """Trae la ventana al frente y retira el icono de la bandeja si estaba minimizado."""
        if hasattr(self, "tray_service"):
            self.tray_service.stop()
        safe_gui_dispatch(self, self._restore_window)

    def _restore_window(self) -> None:
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))

    def minimize_to_tray(self) -> None:
        """Oculta la ventana y activa el icono en la bandeja para mantener activos los programadores."""
        self.withdraw()
        if hasattr(self, "tray_service"):
            self.tray_service.start()

    def on_close(self) -> None:
        """Detiene limpiamente los workers, la bandeja del sistema y destruye la ventana."""
        if hasattr(self, "tray_service"):
            self.tray_service.stop()
        if hasattr(self, "monitor_service"):
            self.monitor_service.stop()
        if hasattr(self, "scheduler_service"):
            self.scheduler_service.stop()
        self.destroy()
