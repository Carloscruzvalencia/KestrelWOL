"""
Servicio del Sistema Operativo y Red Local (services/system_service.py)
KestrelWOL - Arquitectura Offline-First

Gestiona:
- Instancia única de la aplicación mediante socket local.
- Detección de privilegios de Administrador.
- Inspección pasiva y ultraligera de la tabla ARP (0% consumo de CPU).
- Verificación de estado online/offline sin falsos positivos ni procesos pesados.
"""

import os
from pathlib import Path
import platform
import re
import socket
import subprocess
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.config import (
    SINGLE_INSTANCE_HOST,
    SINGLE_INSTANCE_PORT,
    SINGLE_INSTANCE_RESTORE_MSG,
)

IPV4_SAFE_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


class SystemService:
    # Caché compartida de la tabla ARP para evitar llamadas repetidas al sistema
    _arp_cache: Dict[str, str] = {}
    _arp_cache_time: float = 0.0
    _arp_lock = threading.Lock()
    ARP_CACHE_TTL_SECONDS = 6.0

    @staticmethod
    def is_admin() -> bool:
        """Comprueba si la app se ejecuta con permisos de Administrador."""
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    @staticmethod
    def secure_file_permissions(filepath: Path) -> None:
        """
        Aplica permisos NTFS restringidos en Windows (icacls) para que solo el
        usuario actual y Administradores tengan acceso de lectura/escritura (CWE-732).
        """
        if platform.system().lower() != "windows" or not filepath.exists():
            return
        try:
            username = os.environ.get("USERNAME", "")
            if not username:
                return
            # Elimina permisos heredados e impone acceso exclusivo al usuario y Administradores
            subprocess.run(
                [
                    "icacls", str(filepath),
                    "/inheritance:r",
                    "/grant:r", f"{username}:(F)",
                    "/grant:r", "*S-1-5-32-544:(F)"
                ],
                capture_output=True,
                creationflags=0x08000000,
                timeout=3.0
            )
        except Exception:
            pass

    @staticmethod
    def setup_single_instance(
        on_restore_callback: Optional[Callable[[], None]] = None
    ) -> Tuple[bool, Optional[socket.socket]]:
        """
        Garantiza que solo exista una ventana abierta a la vez.
        Si ya existe una, le envía la orden de restaurarse y devuelve (False, None).
        Si es la primera, abre el puerto local y devuelve (True, socket).
        """
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            lock_socket.bind((SINGLE_INSTANCE_HOST, SINGLE_INSTANCE_PORT))
            lock_socket.listen(5)
        except OSError:
            # Otra instancia ya está en ejecución: la traemos al frente y salimos
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                s.connect((SINGLE_INSTANCE_HOST, SINGLE_INSTANCE_PORT))
                s.sendall(SINGLE_INSTANCE_RESTORE_MSG)
                s.close()
            except Exception:
                pass
            return False, None

        if on_restore_callback:
            def listener():
                while True:
                    try:
                        conn, addr = lock_socket.accept()
                        # Verificación estricta de origen local anti-spoofing
                        if addr[0] not in ("127.0.0.1", "localhost"):
                            conn.close()
                            continue
                        data = conn.recv(16)
                        conn.close()
                        if SINGLE_INSTANCE_RESTORE_MSG in data:
                            on_restore_callback()
                    except Exception:
                        break

            threading.Thread(target=listener, daemon=True).start()

        return True, lock_socket

    @classmethod
    def get_arp_table(cls, force_refresh: bool = False) -> Dict[str, str]:
        """
        Obtiene un mapa {ip: mac} de la tabla ARP del sistema con caché de 6 segundos.
        Esto elimina la sobrecarga de CPU y evita crear procesos innecesarios.
        """
        with cls._arp_lock:
            now = time.time()
            if not force_refresh and (now - cls._arp_cache_time) < cls.ARP_CACHE_TTL_SECONDS:
                return dict(cls._arp_cache)

            table: Dict[str, str] = {}
            try:
                flags = 0x08000000 if platform.system().lower() == "windows" else 0
                output = subprocess.check_output(["arp", "-a"], text=True, creationflags=flags)
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) >= 2 and "." in parts[0] and ("-" in parts[1] or ":" in parts[1]):
                        ip = parts[0].strip()
                        mac = parts[1].strip().replace("-", ":").lower()
                        table[ip] = mac
            except Exception:
                pass

            cls._arp_cache = table
            cls._arp_cache_time = now
            return dict(cls._arp_cache)

    @classmethod
    def get_arp_devices(cls, ignored_ips: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Devuelve la lista de dispositivos activos en la red LAN local leídos de la tabla ARP.
        Filtra automáticamente IPs de broadcast e IPs marcadas como ignoradas.
        """
        devices = []
        ignored = set(ignored_ips or [])
        arp_map = cls.get_arp_table(force_refresh=True)

        for ip, mac in arp_map.items():
            if ip.endswith(".255") or ip.startswith("224.") or ip.startswith("239.") or ip in ignored:
                continue
            devices.append({
                "ip": ip,
                "mac": mac,
                "host": "Dispositivo de red",
                "type": "💻 Red LAN"
            })
        return devices

    @classmethod
    def check_machine_status(cls, ip: Optional[str], mac: Optional[str] = None) -> str:
        """
        Verificación de estado ultrarrápida (0% CPU, sin procesos continuos de ping):
        1. Comprueba si el host responde en puertos TCP comunes (445 SMB, 135 RPC, 3389 RDP).
           Un ACK o RST inmediato confirma que la máquina está encendida en < 20 ms.
        2. Valida contra la tabla ARP para evitar falsos positivos por IP duplicada.
        3. Si la MAC de la IP no coincide con la esperada, se marca como 'offline'.
        """
        if not ip:
            return "error"

        clean_expected_mac = mac.replace("-", ":").lower() if mac else None

        # 1. Comprobación rápida por sockets TCP (0 subprocesos creados)
        is_responsive = False
        for port in (445, 135, 3389):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.12)  # 120 ms máximo
                res = s.connect_ex((ip, port))
                s.close()
                # 0 = Conexión aceptada | 10061/ECONNREFUSED = Máquina encendida rechazó el puerto
                if res in (0, 10061, 10054):
                    is_responsive = True
                    break
            except Exception:
                pass

        # 2. Validación cruzada con la tabla ARP para descartar falsos positivos
        arp_table = cls.get_arp_table()
        arp_mac = arp_table.get(ip)

        if arp_mac and clean_expected_mac:
            # Si la IP respondió pero la MAC pertenece a otro equipo, es un falso positivo
            if arp_mac != clean_expected_mac:
                return "offline"
            return "online"

        if is_responsive:
            return "online"

        # 3. Si no respondió por TCP ni está en ARP, hacemos un ping ligero único de sondeo
        try:
            is_win = platform.system().lower() == "windows"
            cmd = ["ping", "-n", "1", "-w", "200", ip] if is_win else ["ping", "-c", "1", "-W", "1", ip]
            flags = 0x08000000 if is_win else 0
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags, timeout=0.5)
            if res.returncode == 0:
                # Comprobar ARP una vez más tras el ping
                updated_arp = cls.get_arp_table(force_refresh=True)
                updated_mac = updated_arp.get(ip)
                if updated_mac and clean_expected_mac and updated_mac != clean_expected_mac:
                    return "offline"
                return "online"
        except Exception:
            pass

        return "offline"

    # --------------------------------------------------------------------------
    # 4. COMPROBACIÓN DE SERVICIOS REMOTOS ESPECÍFICOS (RDP, SSH, VNC, WEB)
    # --------------------------------------------------------------------------
    @classmethod
    def check_machine_services(cls, ip: str, timeout: float = 0.25) -> Dict[str, bool]:
        """
        Escanea puertos de servicios estándar en una máquina encendida:
        - RDP: 3389
        - SSH: 22
        - VNC: 5900
        - WEB: 80 / 443 / 8080
        Retorna un diccionario indicando la disponibilidad de cada servicio.
        """
        if not ip:
            return {"rdp": False, "ssh": False, "vnc": False, "web": False}

        results = {"rdp": False, "ssh": False, "vnc": False, "web": False}
        ports_map = {
            "rdp": [3389],
            "ssh": [22],
            "vnc": [5900],
            "web": [80, 443, 8080],
        }

        for srv, ports in ports_map.items():
            for port in ports:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    code = s.connect_ex((ip, port))
                    s.close()
                    if code == 0:
                        results[srv] = True
                        break
                except Exception:
                    pass

        return results

    # --------------------------------------------------------------------------
    # 5. CONEXIÓN RÁPIDA REMOTA (RDP / SSH / VNC / NAVEGADOR) - HARDENED
    # --------------------------------------------------------------------------
    @staticmethod
    def launch_rdp(ip: str) -> Tuple[bool, str]:
        """Lanza el cliente nativo de Escritorio Remoto con validación estricta de IP."""
        if not ip or not isinstance(ip, str):
            return False, "Dirección IP no válida."
        clean_ip = ip.strip()
        if not IPV4_SAFE_REGEX.match(clean_ip):
            return False, f"IP '{clean_ip}' rechazada: formato IPv4 inseguro o inválido."
        try:
            cmd = ["mstsc", f"/v:{clean_ip}"]
            subprocess.Popen(cmd)
            return True, f"Iniciando sesión RDP hacia {clean_ip}..."
        except Exception as e:
            return False, f"Error al abrir cliente RDP: {e}"

    @staticmethod
    def launch_ssh(ip: str, user: Optional[str] = None) -> Tuple[bool, str]:
        """
        Abre una consola interactiva para SSH de forma segura:
        - Sanitización anti-Command Injection (CWE-78): 0% shell=True.
        - Validación estricta de IPv4 y caracteres alfanuméricos de usuario.
        """
        if not ip or not isinstance(ip, str):
            return False, "Dirección IP no válida."
        clean_ip = ip.strip()
        if not IPV4_SAFE_REGEX.match(clean_ip):
            return False, f"IP '{clean_ip}' rechazada: formato IPv4 inseguro o inválido."

        clean_user = None
        if user:
            clean_user = str(user).strip()
            if not re.match(r"^[a-zA-Z0-9._-]+$", clean_user):
                return False, "Nombre de usuario SSH rechazado: contiene caracteres no permitidos."

        target = f"{clean_user}@{clean_ip}" if clean_user else clean_ip

        try:
            # CREATE_NEW_CONSOLE (0x00000010) abre una ventana de terminal independiente
            # sin requerir 'start' ni shell=True, eliminando cualquier vector de inyección
            creation_flags = 0x00000010 if platform.system().lower() == "windows" else 0
            cmd = ["cmd.exe", "/k", "ssh", target]
            subprocess.Popen(cmd, creationflags=creation_flags)
            return True, f"Abriendo consola SSH hacia {target}..."
        except Exception as e:
            return False, f"Error al iniciar consola SSH: {e}"

    # --------------------------------------------------------------------------
    # 6. APAGADO Y REINICIO REMOTO (GRACEFUL SHUTDOWN) - HARDENED
    # --------------------------------------------------------------------------
    @staticmethod
    def remote_power_action(ip: str, action: str = "shutdown", timeout_sec: int = 30) -> Tuple[bool, str]:
        """
        Ejecuta apagado o reinicio remoto controlado con validación estricta de IP.
        """
        if not ip or not isinstance(ip, str):
            return False, "Dirección IP no válida."
        clean_ip = ip.strip()
        if not IPV4_SAFE_REGEX.match(clean_ip):
            return False, f"IP '{clean_ip}' rechazada: formato IPv4 inseguro o inválido."

        is_reboot = (action.lower() == "reboot")
        flag = "/r" if is_reboot else "/s"
        comment = "Reinicio remoto programado desde Wake On LAN Controller" if is_reboot else "Apagado remoto solicitado desde Wake On LAN Controller"
        safe_timeout = max(0, min(int(timeout_sec), 300))

        cmd = [
            "shutdown",
            "/m", f"\\\\{clean_ip}",
            flag,
            "/t", str(safe_timeout),
            "/c", comment,
            "/f"
        ]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=0x08000000 if platform.system().lower() == "windows" else 0,
                timeout=6.0
            )
            if res.returncode == 0:
                action_name = "Reinicio" if is_reboot else "Apagado"
                return True, f"{action_name} ordenado correctamente para {clean_ip} ({safe_timeout}s de margen)."
            else:
                err_text = res.stderr.strip() or res.stdout.strip() or f"Código de error {res.returncode}"
                return False, f"Error al comunicar con {clean_ip}: {err_text}"
        except Exception as e:
            return False, f"Excepción al ejecutar comando de energía remoto: {e}"
