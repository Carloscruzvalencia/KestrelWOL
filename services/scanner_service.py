"""
Servicio de Escaneo y Descubrimiento de Red Local (services/scanner_service.py)
KestrelWOL - Arquitectura Offline-First

Gestiona:
- Detección pasiva de puestos en la red LAN mediante la tabla ARP del kernel.
- Resolución paralela y no bloqueante de nombres de host locales.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import threading
from typing import Callable, Dict, List, Optional

from services.storage_service import StorageService
from services.system_service import SystemService


class ScannerService:
    def __init__(self, storage_service: Optional[StorageService] = None):
        self.storage = storage_service or StorageService()

    def scan_arp_async(
        self,
        on_complete: Callable[[List[Dict[str, str]]], None],
        on_error: Optional[Callable[[str], None]] = None
    ) -> None:
        """
        Escanea la red local en segundo plano sin congelar la ventana.
        Devuelve la lista de equipos encontrados con su IP, MAC y nombre de host.
        """
        def worker():
            try:
                ignored_ips = self.storage.load_ignored_ips()
                devices = SystemService.get_arp_devices(ignored_ips=ignored_ips)

                def resolve_name(dev: Dict[str, str]):
                    ip = dev.get("ip")
                    if ip:
                        try:
                            # Intenta resolver el nombre local en menos de 0.5 s
                            host_name = socket.gethostbyaddr(ip)[0]
                            if host_name:
                                dev["host"] = host_name
                        except Exception:
                            dev["host"] = "Dispositivo de red"

                # Resolver nombres en paralelo con hasta 8 hilos rápidos
                with ThreadPoolExecutor(max_workers=8) as executor:
                    futures = [executor.submit(resolve_name, d) for d in devices]
                    for f in as_completed(futures):
                        pass

                on_complete(devices)
            except Exception as e:
                if on_error:
                    on_error(str(e))

        threading.Thread(target=worker, daemon=True).start()
