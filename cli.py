"""
KestrelWOL - Command Line Interface (cli.py)
Automated and headless machine wake utility with safety compliance (Anti-inrush delay & audit logging).
"""

import argparse
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
from services import AuditService, StorageService, SystemService, WolService

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def wake_machines(
    machines_list: Optional[List[Dict[str, Any]]] = None,
    target_zone: Optional[str] = None,
    staggered_delay: float = 0.25
) -> None:
    """
    Despierta los equipos registrados aplicando las directivas de seguridad:
    - Escalonamiento anti-inrush current (250 ms por defecto).
    - Trazabilidad y auditoría forense NIS 2 / ENS.
    """
    storage = StorageService()
    audit = AuditService()
    wol = WolService(audit_service=audit)

    if machines_list is None:
        machines_list = storage.load_machines()

    if not machines_list:
        print("[!] No hay equipos configurados en machines.json.")
        return

    # Filtrar por zona si se especificó
    if target_zone:
        zone_lower = target_zone.strip().lower()
        machines_list = [
            m for m in machines_list
            if (m.get("zone") or "General").strip().lower() == zone_lower
        ]
        if not machines_list:
            print(f"[!] No se encontraron equipos en la zona '{target_zone}'.")
            return

    print(f"[*] Iniciando proceso de arranque para {len(machines_list)} equipo(s)...")
    sent_count = wol.wake_all_sync(machines_list, staggered_delay=staggered_delay)
    print(f"[+] Paquetes mágicos transmitidos: {sent_count}")


def list_machines() -> None:
    """Muestra el inventario de equipos configurados en terminal."""
    storage = StorageService()
    machines = storage.load_machines()
    if not machines:
        print("[i] No hay equipos registrados en machines.json.")
        return

    print(f"\n{'NOMBRE':<22} {'IP':<16} {'MAC':<18} {'ZONA':<14}")
    print("-" * 72)
    for m in machines:
        name = m.get("name", "N/A")
        ip = m.get("ip", "N/A")
        mac = m.get("mac", "N/A")
        zone = m.get("zone", "General")
        print(f"{name:<22} {ip:<16} {mac:<18} {zone:<14}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="kestrelwol",
        description="KestrelWOL - Herramienta CLI de encendido remoto seguro y telemetría de red"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Enciende todos los equipos activos registrados"
    )
    parser.add_argument(
        "--zone",
        type=str,
        default=None,
        help="Filtra y enciende únicamente los equipos pertenecientes a una zona específica"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Retardo en segundos entre envíos UDP (anti-inrush current, defecto: 0.25s)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lista todos los equipos configurados"
    )
    parser.add_argument(
        "--import-csv",
        type=str,
        default=None,
        help="Ruta a un archivo CSV para importar y fusionar equipos"
    )
    parser.add_argument(
        "--export-csv",
        type=str,
        default=None,
        help="Ruta de destino para exportar el inventario de equipos a CSV"
    )
    parser.add_argument(
        "--check-services",
        type=str,
        default=None,
        help="Comprueba puertos y servicios activos en la IP indicada (RDP, SSH, WEB, VNC)"
    )
    parser.add_argument(
        "--shutdown",
        type=str,
        default=None,
        help="Ordena el apagado remoto controlado (30s) a la IP especificada"
    )
    parser.add_argument(
        "--reboot",
        type=str,
        default=None,
        help="Ordena el reinicio remoto controlado (30s) a la IP especificada"
    )

    args = parser.parse_args()
    storage = StorageService()

    if args.list:
        list_machines()
    elif args.import_csv:
        path = Path(args.import_csv)
        added, updated, msg = storage.import_machines_from_csv(path)
        print(f"[*] {msg}")
    elif args.export_csv:
        path = Path(args.export_csv)
        ok, msg = storage.export_machines_to_csv(path)
        print(f"[{'+' if ok else '!'}] {msg}")
    elif args.check_services:
        ip = args.check_services
        print(f"[*] Escaneando servicios estándar en {ip}...")
        res = SystemService.check_machine_services(ip)
        for srv, is_up in res.items():
            icon = "🟢 ACTIVO " if is_up else "🔴 CERRADO"
            print(f"  {icon} - {srv.upper()}")
    elif args.shutdown:
        ip = args.shutdown
        print(f"[*] Solicitando apagado remoto para {ip}...")
        ok, msg = SystemService.remote_power_action(ip, action="shutdown")
        print(f"[{'+' if ok else '!'}] {msg}")
    elif args.reboot:
        ip = args.reboot
        print(f"[*] Solicitando reinicio remoto para {ip}...")
        ok, msg = SystemService.remote_power_action(ip, action="reboot")
        print(f"[{'+' if ok else '!'}] {msg}")
    elif args.zone:
        wake_machines(target_zone=args.zone, staggered_delay=args.delay)
    else:
        # Modo por defecto (o con --all): encender todos los equipos
        wake_machines(staggered_delay=args.delay)


if __name__ == "__main__":
    main()

