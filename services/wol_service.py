"""
Servicio de Wake On LAN y Seguridad Eléctrica (services/wol_service.py)
Cumplimiento: REBT / UNE-EN 62040 (Staggered Wake)
"""

import re
import socket
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.config import STAGGERED_WAKE_DELAY_SECONDS
from services.audit_service import AuditService

IP_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
MAC_REGEX = re.compile(
    r"^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$|^[0-9a-fA-F]{12}$"
)


class WolService:
    """
    Servicio de red de bajo nivel para emisión de paquetes mágicos WOL.
    Garantiza:
    - Sanitización regex estricta antes de abrir sockets.
    - Despacho escalonado desacoplado multihilo anti-inrush.
    """

    def __init__(self, audit_service: Optional[AuditService] = None):
        self.audit = audit_service or AuditService()

    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Sanitización estricta por regex de dirección IPv4."""
        if not ip or not isinstance(ip, str):
            return False
        return bool(IP_REGEX.match(ip.strip()))

    @staticmethod
    def validate_mac(mac: str) -> bool:
        """Sanitización estricta por regex de dirección MAC física."""
        if not mac or not isinstance(mac, str):
            return False
        return bool(MAC_REGEX.match(mac.strip()))

    @staticmethod
    def create_magic_packet(mac_address: str) -> bytes:
        """Construye los 102 bytes del payload Magic Packet (6x0xFF + 16xMAC)."""
        clean_mac = re.sub(r"[^0-9a-fA-F]", "", mac_address)
        if len(clean_mac) != 12:
            raise ValueError(f"MAC inválida para Magic Packet: {mac_address}")
        mac_bytes = bytes.fromhex(clean_mac)
        return b"\xff" * 6 + mac_bytes * 16

    def send_packet(self, mac: str, ip: Optional[str] = None, host_name: str = "N/A") -> Tuple[bool, str]:
        """
        Emite un Magic Packet UDP robusto a través de broadcast global, local y unicast.
        Retorna (éxito, mensaje).
        """
        if not self.validate_mac(mac):
            self.audit.log(
                "WOL_VALIDATION_ERROR",
                target_name=host_name,
                ip=ip or "N/A",
                mac=mac,
                status="ERROR",
                details="MAC rechazada por regex de sanitización"
            )
            return False, "Dirección MAC con formato no válido."

        if ip and not self.validate_ip(ip):
            self.audit.log(
                "WOL_VALIDATION_ERROR",
                target_name=host_name,
                ip=ip,
                mac=mac,
                status="ERROR",
                details="IP rechazada por regex de sanitización"
            )
            return False, "Dirección IP con formato no válido."

        try:
            packet = self.create_magic_packet(mac)
        except Exception as e:
            return False, f"Error al generar paquete mágico: {e}"

        targets = ["255.255.255.255"]
        if ip:
            targets.append(ip)
            parts = ip.split(".")
            if len(parts) == 4:
                targets.append(f"{parts[0]}.{parts[1]}.{parts[2]}.255")

        ports = [9, 7]
        success_count = 0

        for target in set(targets):
            for port in ports:
                sock = None
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.settimeout(1.0)
                    sock.sendto(packet, (target, port))
                    success_count += 1
                except Exception:
                    pass
                finally:
                    if sock:
                        try:
                            sock.close()
                        except Exception:
                            pass

        if success_count > 0:
            self.audit.log(
                "WAKE_ROBUST",
                target_name=host_name,
                ip=ip or "N/A",
                mac=mac,
                status="SUCCESS",
                details=f"Emitido datagrama UDP ({success_count} sockets)"
            )
            return True, f"Paquete enviado exitosamente a {host_name} ({mac})."
        else:
            self.audit.log(
                "WAKE_ROBUST",
                target_name=host_name,
                ip=ip or "N/A",
                mac=mac,
                status="FAILURE",
                details="No se pudo emitir en ninguno de los sockets UDP"
            )
            return False, "Fallo al emitir sockets UDP en la red local."

    def wake_single(self, machine: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Intenta encender un equipo individual enviando los paquetes Magic Packet.
        """
        return self.send_packet(
            mac=machine.get("mac", ""),
            ip=machine.get("ip"),
            host_name=machine.get("name", "N/A")
        )

    def wake_staggered_async(
        self,
        targets: List[Dict[str, Any]],
        on_progress: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
        on_complete: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """
        Ejecuta un encendido escalonado en un hilo desacoplado en segundo plano.
        Aplica un retardo obligatorio de 250 ms entre paquetes UDP (REBT / UNE-EN 62040).
        """
        def worker():
            total = len(targets)
            sent = 0

            self.audit.log(
                "MASS_WAKE_START",
                status="IN_PROGRESS",
                details=f"Iniciando encendido escalonado de {total} puestos"
            )

            for idx, m in enumerate(targets):
                self.send_packet(
                    mac=m.get("mac", ""),
                    ip=m.get("ip"),
                    host_name=m.get("name", "N/A")
                )
                sent += 1
                if on_progress:
                    on_progress(sent, total, m)

                if idx < total - 1:
                    time.sleep(STAGGERED_WAKE_DELAY_SECONDS)

            self.audit.log(
                "MASS_WAKE_COMPLETED",
                status="SUCCESS",
                details=f"Finalizado encendido escalonado de {sent}/{total} puestos"
            )

            if on_complete:
                on_complete(sent, total)

        threading.Thread(target=worker, daemon=True).start()

    def wake_all_sync(
        self,
        targets: List[Dict[str, Any]],
        staggered_delay: float = STAGGERED_WAKE_DELAY_SECONDS
    ) -> int:
        """
        Ejecuta un encendido escalonado de forma síncrona (ideal para scripts CLI o automatizaciones).
        Aplica retardo anti-inrush entre envíos.
        Retorna la cantidad de paquetes enviados.
        """
        sent = 0
        total = len(targets)

        for idx, m in enumerate(targets):
            self.send_packet(
                mac=m.get("mac", ""),
                ip=m.get("ip"),
                host_name=m.get("name", "N/A")
            )
            sent += 1
            if idx < total - 1 and staggered_delay > 0:
                time.sleep(staggered_delay)

        return sent
