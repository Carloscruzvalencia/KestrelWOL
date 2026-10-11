"""
Servicio de Persistencia y Normalización Canónica (services/storage_service.py)
KestrelWOL - Arquitectura Offline-First
"""

import csv
import datetime
import json
from pathlib import Path
import re
import threading
from typing import Any, Dict, List, Optional, Tuple

from core.config import (
    APP_VERSION,
    IGNORED_FILE,
    MACHINES_FILE,
    TERMS_FILE,
)
from services.system_service import SystemService


class StorageService:
    """
    Gestiona la persistencia de datos en archivos JSON locales de forma atómica y thread-safe.
    Garantiza la normalización canónica de zonas para evitar fragmentación ('a' vs 'A').
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StorageService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._file_lock = threading.Lock()
        self._initialized = True

    @staticmethod
    def _sanitize_csv_cell(val: Any) -> str:
        """
        Previene ataques de CSV Formula Injection / DDE (CWE-1236).
        Si un valor comienza con =, +, -, @ o caracteres de control,
        se antepone un apóstrofe (') para forzar a hojas de cálculo a tratarlo como texto plano.
        """
        s = str(val if val is not None else "")
        if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
            return f"'{s}"
        return s

    @staticmethod
    def _desanitize_csv_cell(val: str) -> str:
        """Elimina el escape de apóstrofe introducido por sanitización previa."""
        s = str(val or "").strip()
        if s.startswith("'") and len(s) > 1 and s[1] in ("=", "+", "-", "@", "\t", "\r"):
            return s[1:]
        return s

    # --------------------------------------------------------------------------
    # 1. NORMALIZACIÓN CANÓNICA DE ZONAS
    # --------------------------------------------------------------------------
    def canonicalize_zone(self, raw_zone: Optional[str], machines: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Normaliza de manera canónica e insensible a mayúsculas/minúsculas el nombre de zona.
        Si ya existe una zona con los mismos caracteres (ej. 'Zona A' frente a 'zona a' o 'A' frente a 'a'),
        se adopta la grafía existente para evitar presets duplicados.
        """
        if not raw_zone or not str(raw_zone).strip():
            return "General"

        cleaned = str(raw_zone).strip()
        cleaned_lower = cleaned.lower()

        current_machines = machines if machines is not None else self.load_machines()

        # Buscar coincidencia exacta case-insensitive en las máquinas registradas
        for m in current_machines:
            existing = (m.get("zone") or "General").strip()
            if existing.lower() == cleaned_lower:
                return existing

        # Si es nueva y tiene longitud 1 (ej: 'a' -> 'A')
        if len(cleaned) == 1:
            return cleaned.upper()

        # Si empieza por 'zona ' (ej: 'zona b' -> 'Zona B')
        if cleaned_lower.startswith("zona "):
            suffix = cleaned[5:].strip()
            if len(suffix) == 1:
                return f"Zona {suffix.upper()}"
            return f"Zona {suffix.title()}"

        # Capitalización estándar
        return cleaned[:1].upper() + cleaned[1:]

    def get_existing_zones(self, machines: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """Devuelve la lista alfabética de zonas únicas registradas."""
        current_machines = machines if machines is not None else self.load_machines()
        seen: Dict[str, str] = {}
        for m in current_machines:
            z = (m.get("zone") or "General").strip()
            if z:
                k = z.lower()
                if k not in seen:
                    seen[k] = z

        if not seen:
            return ["Zona A", "Zona B"]
        return sorted(list(seen.values()), key=lambda s: s.lower())

    # --------------------------------------------------------------------------
    # 2. PERSISTENCIA DE MÁQUINAS (machines.json)
    # --------------------------------------------------------------------------
    def load_machines(self) -> List[Dict[str, Any]]:
        with self._file_lock:
            if not MACHINES_FILE.exists():
                return []
            try:
                with open(MACHINES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Normalizar zonas al cargar
                        for item in data:
                            if isinstance(item, dict):
                                z = (item.get("zone") or "General").strip()
                                item["zone"] = self.canonicalize_zone(z, data)
                        return data
            except Exception:
                return []
        return []

    def save_machines(self, machines: List[Dict[str, Any]]) -> bool:
        with self._file_lock:
            try:
                # Normalizar zonas de todas las máquinas antes de escribir
                for m in machines:
                    if isinstance(m, dict):
                        m["zone"] = self.canonicalize_zone(m.get("zone", "General"), machines)

                temp_file = MACHINES_FILE.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(machines, f, indent=4, ensure_ascii=False)
                temp_file.replace(MACHINES_FILE)
                SystemService.secure_file_permissions(MACHINES_FILE)
                return True
            except Exception:
                return False

    # --------------------------------------------------------------------------
    # 3. TÉRMINOS LEGALES (terms_accepted.json)
    # --------------------------------------------------------------------------
    def is_terms_accepted(self) -> bool:
        with self._file_lock:
            if not TERMS_FILE.exists():
                return False
            try:
                with open(TERMS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return bool(data.get("accepted"))
            except Exception:
                return False

    def save_terms_accepted(self, operator_user: str) -> bool:
        with self._file_lock:
            try:
                payload = {
                    "accepted": True,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "operator_user": operator_user,
                    "version": APP_VERSION,
                }
                with open(TERMS_FILE, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=4)
                return True
            except Exception:
                return False

    # --------------------------------------------------------------------------
    # 4. IPS IGNORADAS DEL ESCÁNER (ignored.json)
    # --------------------------------------------------------------------------
    def load_ignored_ips(self) -> List[str]:
        with self._file_lock:
            if not IGNORED_FILE.exists():
                return []
            try:
                with open(IGNORED_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception:
                return []

    def save_ignored_ips(self, ips: List[str]) -> bool:
        with self._file_lock:
            try:
                with open(IGNORED_FILE, "w", encoding="utf-8") as f:
                    json.dump(ips, f, indent=4)
                return True
            except Exception:
                return False

    # --------------------------------------------------------------------------
    # 5. IMPORTACIÓN Y EXPORTACIÓN DE INVENTARIO (CSV)
    # --------------------------------------------------------------------------
    def export_machines_to_csv(self, filepath: Path) -> Tuple[bool, str]:
        """
        Exporta el inventario completo de equipos a formato CSV estándar.
        Cabeceras: name,ip,mac,zone,schedule_enabled,schedule_time,schedule_days
        """
        machines = self.load_machines()
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "name", "ip", "mac", "zone",
                    "schedule_enabled", "schedule_time", "schedule_days"
                ])
                for m in machines:
                    sched = m.get("schedule") or {}
                    days_str = ";".join(str(d) for d in sched.get("days", []))
                    writer.writerow([
                        self._sanitize_csv_cell(m.get("name", "")),
                        self._sanitize_csv_cell(m.get("ip", "")),
                        self._sanitize_csv_cell(m.get("mac", "")),
                        self._sanitize_csv_cell(m.get("zone", "General")),
                        "true" if sched.get("enabled") else "false",
                        self._sanitize_csv_cell(sched.get("time", "")),
                        self._sanitize_csv_cell(days_str)
                    ])
            return True, f"Inventario exportado exitosamente ({len(machines)} equipos)."
        except Exception as e:
            return False, f"Error al exportar archivo CSV: {e}"

    def import_machines_from_csv(self, filepath: Path) -> Tuple[int, int, str]:
        """
        Importa y fusiona equipos desde un archivo CSV con validación estricta de sintaxis.
        Devuelve: (nuevos_añadidos, actualizados, mensaje_resumen).
        """
        if not filepath.exists():
            return 0, 0, "El archivo especificado no existe."

        mac_regex = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
        ip_regex = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")

        current_machines = self.load_machines()
        # Mapeo por MAC normalizada
        machines_by_mac = {
            m.get("mac", "").replace("-", ":").lower(): m
            for m in current_machines if m.get("mac")
        }

        added = 0
        updated = 0
        invalid_rows = 0

        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    return 0, 0, "El archivo CSV está vacío o no tiene encabezados válidos."

                # Normalizar nombres de columnas (minúsculas y sin espacios)
                col_map = {c.strip().lower(): c for c in reader.fieldnames}

                for row_idx, row in enumerate(reader, start=2):
                    # Obtener campos tolerando variaciones y desescapando fórmulas
                    raw_name = (row.get(col_map.get("name", "")) or row.get("nombre") or "").strip()
                    raw_ip = (row.get(col_map.get("ip", "")) or "").strip()
                    raw_mac = (row.get(col_map.get("mac", "")) or "").strip()
                    raw_zone = (row.get(col_map.get("zone", "")) or row.get("zona") or "General").strip()

                    name = re.sub(r"[\x00-\x1f\x7f]", "", self._desanitize_csv_cell(raw_name))[:64].strip()
                    ip = self._desanitize_csv_cell(raw_ip)
                    mac = self._desanitize_csv_cell(raw_mac)
                    zone = re.sub(r"[\x00-\x1f\x7f]", "", self._desanitize_csv_cell(raw_zone))[:40].strip() or "General"

                    if not name or not ip or not mac:
                        invalid_rows += 1
                        continue

                    # Validación de formato IP y MAC estricta
                    if not ip_regex.match(ip) or not mac_regex.match(mac):
                        invalid_rows += 1
                        continue

                    norm_mac = mac.replace("-", ":").lower()

                    sched_en = (row.get(col_map.get("schedule_enabled", "")) or "").strip().lower() in ("1", "true", "yes", "si", "sí")
                    sched_time = (row.get(col_map.get("schedule_time", "")) or "").strip()
                    days_raw = (row.get(col_map.get("schedule_days", "")) or "").strip()
                    days_list: List[int] = []
                    if days_raw:
                        for token in re.split(r"[,;|\s]+", days_raw):
                            if token.isdigit() and 0 <= int(token) <= 6:
                                days_list.append(int(token))

                    machine_data = {
                        "name": name,
                        "ip": ip,
                        "mac": norm_mac,
                        "zone": self.canonicalize_zone(zone, current_machines),
                        "schedule": {
                            "enabled": sched_en,
                            "time": sched_time or "08:00",
                            "days": sorted(list(set(days_list))) if days_list else [0, 1, 2, 3, 4]
                        }
                    }

                    if norm_mac in machines_by_mac:
                        # Actualizar equipo existente
                        machines_by_mac[norm_mac].update(machine_data)
                        updated += 1
                    else:
                        machines_by_mac[norm_mac] = machine_data
                        current_machines.append(machine_data)
                        added += 1

            if added > 0 or updated > 0:
                self.save_machines(current_machines)

            msg = f"Importación completada: {added} nuevos añadidos, {updated} actualizados."
            if invalid_rows > 0:
                msg += f" ({invalid_rows} filas omitidas por formato inválido)."
            return added, updated, msg
        except Exception as e:
            return 0, 0, f"Error al procesar el archivo CSV: {e}"

