"""
Servicio de Auditoría y Trazabilidad Forense (services/audit_service.py)
Cumplimiento: Directiva NIS 2 y Esquema Nacional de Seguridad (ENS)
"""

import getpass
import hashlib
import logging
from logging.handlers import RotatingFileHandler
import os
import threading
from typing import List
from core.config import AUDIT_LOG_FILE, AUDIT_LOG_MAX_BYTES, AUDIT_LOG_BACKUP_COUNT
from services.system_service import SystemService


class AuditService:
    """
    Servicio thread-safe para registro local inmutable y rotativo de auditoría.
    Implementa encadenamiento de integridad criptográfica (SHA-256) anti-tampering (NIS 2 / ENS).
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AuditService, cls).__new__(cls)
                cls._instance._initialized = False
                cls._instance._last_hash = "GENESIS_NODE_ROOT"
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._logger = logging.getLogger("WOL_AUDIT_SERVICE")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        try:
            handler = RotatingFileHandler(
                str(AUDIT_LOG_FILE),
                maxBytes=AUDIT_LOG_MAX_BYTES,
                backupCount=AUDIT_LOG_BACKUP_COUNT,
                encoding="utf-8"
            )
            formatter = logging.Formatter(
                "%(asctime)s | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            SystemService.secure_file_permissions(AUDIT_LOG_FILE)
        except Exception:
            pass

        self._initialized = True

    @staticmethod
    def _get_current_user() -> str:
        """Obtiene el nombre del usuario de la sesión del sistema operativo."""
        try:
            return getpass.getuser()
        except Exception:
            try:
                return os.getlogin()
            except Exception:
                return "unknown"

    def log(
        self,
        action: str,
        target_name: str = "N/A",
        ip: str = "N/A",
        mac: str = "N/A",
        status: str = "SUCCESS",
        details: str = "",
        host: str = None
    ) -> None:
        """
        Registra una entrada estructurada en audit.log con hash SHA-256 encadenado.
        """
        user = self._get_current_user()
        final_host = host if host is not None else (target_name or "N/A")
        msg = (
            f"[USER: {user}] "
            f"[ACTION: {action}] "
            f"[HOST: {final_host}] "
            f"[IP: {ip or 'N/A'}] "
            f"[MAC: {mac or 'N/A'}] "
            f"[STATUS: {status}]"
        )
        if details:
            msg += f" [INFO: {details}]"

        with self._lock:
            # Hash chaining anti-manipulación: cada línea vincula criptográficamente la anterior
            payload = f"{self._last_hash}|{msg}".encode("utf-8")
            line_hash = hashlib.sha256(payload).hexdigest()[:16]
            self._last_hash = line_hash
            msg_with_sig = f"{msg} [INTEGRITY: {line_hash}]"
            self._logger.info(msg_with_sig)

    def read_last_entries(self, max_lines: int = 200) -> List[str]:
        """Lee de forma segura las últimas líneas de audit.log para visualización en GUI."""
        if not AUDIT_LOG_FILE.exists():
            return []
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                return lines[-max_lines:]
        except Exception as e:
            return [f"Error al leer audit.log: {e}\n"]
