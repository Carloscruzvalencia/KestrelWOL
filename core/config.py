"""
Módulo de Configuración Central y Parámetros del Sistema (core/config.py)
KestrelWOL - Arquitectura Offline-First

Define constantes inmutables, rutas relativas al entorno de ejecución,
paleta cromática temática Slate Dark, tipografías, dimensiones y políticas de seguridad.
"""

import os
from pathlib import Path
from typing import Dict, Tuple

# ==============================================================================
# 1. RUTAS Y ARCHIVOS DEL SISTEMA (ESTRICTO OFFLINE-FIRST)
# ==============================================================================
BASE_DIR: Path = Path(os.path.dirname(os.path.abspath(__file__))).parent.resolve()
DATA_DIR: Path = BASE_DIR / "data"
DOCS_DIR: Path = BASE_DIR / "docs"
EXAMPLES_DIR: Path = BASE_DIR / "examples"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Migración transparente de archivos de datos a la subcarpeta data/
    for _legacy in ("machines.json", "ignored.json", "terms_accepted.json", "audit.log"):
        _old = BASE_DIR / _legacy
        _new = DATA_DIR / _legacy
        if _old.exists() and not _new.exists():
            try:
                _old.replace(_new)
            except Exception:
                pass
except Exception:
    pass

MACHINES_FILE: Path = DATA_DIR / "machines.json"
IGNORED_FILE: Path = DATA_DIR / "ignored.json"
TERMS_FILE: Path = DATA_DIR / "terms_accepted.json"
AUDIT_LOG_FILE: Path = DATA_DIR / "audit.log"

# ==============================================================================
# 2. IDENTIDAD Y CONTROL DE INSTANCIA ÚNICA
# ==============================================================================
APP_TITLE: str = "KestrelWOL"
APP_VERSION: str = "1.0.0"
APP_SUBTITLE: str = "Panel de encendido remoto y telemetría de red"

SINGLE_INSTANCE_HOST: str = "127.0.0.1"
SINGLE_INSTANCE_PORT: int = 47830
SINGLE_INSTANCE_RESTORE_MSG: bytes = b"RESTORE"

# ==============================================================================
# 3. DIRECTIVAS DE SEGURIDAD, ELÉCTRICAS Y CIBERSEGURIDAD
# ==============================================================================
# REBT / UNE-EN 62040: Retardo escalonado (anti inrush-current)
STAGGERED_WAKE_DELAY_SECONDS: float = 0.25  # 250 ms entre paquetes UDP

# NIS 2 / ENS: Rotación de logs de auditoría forense
AUDIT_LOG_MAX_BYTES: int = 2 * 1024 * 1024  # 2 MB por archivo
AUDIT_LOG_BACKUP_COUNT: int = 5             # Hasta 5 rotaciones históricas

# Temporizadores de Workers en Segundo Plano
MONITOR_INTERVAL_SECONDS: float = 12.0      # Ciclo de escaneo de estado
MONITOR_ITEM_SLEEP_SECONDS: float = 0.3     # Pausa entre pings para 0% picos de CPU
SCHEDULE_CHECK_INTERVAL_SECONDS: float = 15.0 # Verificación de encendido programado

# ==============================================================================
# 4. PALETA DE COLORES (THEME: INDUSTRIAL ENTERPRISE DARK MODE)
# ==============================================================================
# Fondos y Superficies Neutras (Obsidian / Neutral-Black)
BG_DARK: str = "#090A0D"              # Fondo principal de la aplicación
BG_CARD: str = "#111318"              # Superficies elevadas (tarjetas, cabecera, modales)
BG_ROW: str = "#161920"               # Filas interactivas / contenedores activos
BG_INPUT: str = "#161920"             # Campos de entrada
BG_CONTAINER_DARK: str = "#0D0F14"    # Cajas de telemetría, terminales y logs
BG_BTN_SECONDARY: str = "#1A1E26"     # Botones secundarios y acciones de tarjeta
BG_BORDER: str = "#222630"            # Borde hairline por defecto (1px)
BG_BORDER_HOVER: str = "#2E3440"      # Borde hairline en hover (1px)
BG_BORDER_BUTTON: str = "#2A303C"     # Borde hairline para botones secundarios (1px)

# Tipografías y Contrastes
TEXT_PRIMARY: str = "#F8FAFC"         # Texto principal
TEXT_SECONDARY: str = "#E2E8F0"       # Texto off-white para acciones secundarias
TEXT_MUTED: str = "#94A3B8"           # Texto secundario / descriptivo
TEXT_DISABLED: str = "#64748B"        # Cabeceras de columna / deshabilitados

# Colores de Acento y Estados Operativos
ACCENT_EMERALD: str = "#10B981"       # Acento primario global y estado activo
HOVER_EMERALD: str = "#059669"        # Hover primario
BUTTON_PRIMARY_TEXT: str = "#090A0D"  # Texto de alto contraste sobre acento esmeralda

ACCENT_BLUE: str = "#3B82F6"          # Indicador informativo / sondeo
ACCENT_ROSE: str = "#EF4444"          # Offline / acción destructiva en hover
ACCENT_AMBER: str = "#F59E0B"         # Alertas / programado
ACCENT_SKY: str = "#94A3B8"           # Enlaces / metadata neutra

# Colores de Hover (Interactividad)
HOVER_BLUE: str = "#2563EB"
HOVER_ROSE: str = "#EF4444"
HOVER_AMBER: str = "#D97706"
HOVER_SECONDARY: str = "#232834"      # Hover sutil para botones #1A1E26

# Radio de bordes consistente
UI_RADIUS: int = 6

# Estados de Monitor / Puestos (Micro-etiquetas en mayúsculas + punto 6px)
STATUS_COLORS: Dict[str, Dict[str, str]] = {
    "online": {
        "text": "ONLINE",
        "dot": "#10B981",
        "bg": "#161920",
        "fg": "#10B981",
        "icon_fill": "#0D1E18",
        "icon_outline": "#10B981",
    },
    "offline": {
        "text": "OFFLINE",
        "dot": "#EF4444",
        "bg": "#161920",
        "fg": "#94A3B8",
        "icon_fill": "#1A1114",
        "icon_outline": "#EF4444",
    },
    "error": {
        "text": "ALERTA",
        "dot": "#F59E0B",
        "bg": "#161920",
        "fg": "#F59E0B",
        "icon_fill": "#1E180E",
        "icon_outline": "#F59E0B",
    },
    "pending": {
        "text": "SONDEO",
        "dot": "#3B82F6",
        "bg": "#161920",
        "fg": "#94A3B8",
        "icon_fill": "#161920",
        "icon_outline": "#475569",
    },
}

# ==============================================================================
# 5. TIPOGRAFÍAS Y FUENTES NATIVAS
# ==============================================================================
FONT_FAMILY_MAIN: str = "Segoe UI"
FONT_FAMILY_MONO: str = "Consolas"

FONTS = {
    "title_main": (FONT_FAMILY_MAIN, 15, "bold"),
    "title_section": (FONT_FAMILY_MAIN, 11, "bold"),
    "title_card": (FONT_FAMILY_MAIN, 12, "bold"),
    "body_bold": (FONT_FAMILY_MAIN, 10, "bold"),
    "body_normal": (FONT_FAMILY_MAIN, 10),
    "caption_bold": (FONT_FAMILY_MAIN, 9, "bold"),
    "caption_normal": (FONT_FAMILY_MAIN, 9),
    "micro": (FONT_FAMILY_MAIN, 8, "bold"),
    "mono_data": (FONT_FAMILY_MONO, 11),
    "mono_log": (FONT_FAMILY_MONO, 10),
    "clock_large": (FONT_FAMILY_MAIN, 16, "bold"),
}

# ==============================================================================
# 6. DIMENSIONES Y BREAKPOINTS RESPONSIVE
# ==============================================================================
WINDOW_DEFAULT_SIZE: str = "860x700"
WINDOW_MIN_WIDTH: int = 780
WINDOW_MIN_HEIGHT: int = 600

# Responsive Columns Breakpoint
BREAKPOINT_THREE_COLUMNS: int = 1320  # Si width >= 1320px -> 3 cols, sino 2 cols

# Dimensiones de Diálogos Modales
MODAL_SIZES: Dict[str, Tuple[int, int]] = {
    "legal_terms": (720, 620),
    "safety_confirm": (560, 440),
    "audit_viewer": (780, 480),
    "device_edit": (420, 430),
    "schedule": (520, 460),
    "scanner": (750, 520),
    "ignored_manager": (350, 450),
}

# ==============================================================================
# 7. TEXTOS LEGALES Y CLÁUSULAS NORMATIVAS (EULA / RD 1215/1997 / REBT)
# ==============================================================================
EULA_BANNER_TEXT: str = (
    "EULA: No apto para control de parada de emergencia ni entornos con riesgo físico "
    "(non-fail-safe). Distribución 'AS IS' bajo Directiva 2006/42/CE & REBT."
)

LEGAL_TERMS_FULL_TEXT: str = (
    "========================================================================================\n"
    "ACUERDO DE LICENCIA Y CONDICIONES DE OPERACIÓN SEGURA (EULA & INDUSTRIAL COMPLIANCE)\n"
    "========================================================================================\n\n"
    "1. SEGURIDAD OPERATIVA Y MAQUINARIA (Directiva 2006/42/CE / RD 1215/1997)\n"
    "   ------------------------------------------------------------------------------------\n"
    "   • SISTEMA NON-FAIL-SAFE: Este software NO es apto para control de parada de emergencia\n"
    "     ni para su uso en entornos con riesgo físico directo a personas o bienes.\n"
    "   • CONFIRMACIÓN OBLIGATORIA: Todo encendido masivo o por zonas exige confirmación previa\n"
    "     certificando que el entorno físico se encuentra despejado.\n\n"
    "2. INFRAESTRUCTURA ELÉCTRICA Y EQUIPOS DE TRABAJO (REBT / UNE-EN 62040)\n"
    "   ------------------------------------------------------------------------------------\n"
    "   • PROTECCIÓN CONTRA INRUSH CURRENT: El encendido simultáneo de fuentes de alimentación de PC\n"
    "     produce picos de corriente transitorios capaces de disparar protecciones magnetotérmicas\n"
    "     o sobrecargar SAIs/UPS. Este software implementa un envío escalonado automático\n"
    "     (staggered wake) con un retardo de 250 ms entre cada paquete UDP en bucles globales.\n\n"
    "3. CIBERSEGURIDAD Y TRAZABILIDAD (Directiva NIS 2 / Esquema Nacional de Seguridad - ENS)\n"
    "   ------------------------------------------------------------------------------------\n"
    "   • REGISTRO DE AUDITORÍA FORENSE: Cada paquete transmitido o intento bloqueado es registrado\n"
    "     en el archivo local rotativo 'audit.log' (max 2MB, 5 rotaciones) junto con el timestamp ISO,\n"
    "     el usuario del sistema operativo ejecutor, la IP, la MAC y el resultado de la acción.\n"
    "   • SANITIZACIÓN ESTRICTA: Las direcciones IP y MAC se validan mediante expresiones regulares\n"
    "     estrictas antes de la apertura o emisión de sockets UDP en la pila de red.\n\n"
    "4. RESPONSABILIDAD CIVIL Y CONTRACTUAL (DISTRIBUCIÓN 'AS IS')\n"
    "   ------------------------------------------------------------------------------------\n"
    "   • EXONERACIÓN LEGAL: El software se distribuye 'TAL CUAL' ('AS IS'), sin garantías de ninguna\n"
    "     clase, explícitas o implícitas, sobre disponibilidad continua o respuesta eléctrica.\n"
    "   • ALCANCE TÉCNICO: La aplicación se limita estrictamente a emitir datagramas UDP Magic Packet\n"
    "     en la red local estándar. La responsabilidad íntegra de verificar que el área de los puestos\n"
    "     esté despejada antes de su activación recae al 100% en el operador humano.\n"
    "   • MÍNIMO PRIVILEGIO: El software está concebido para ejecutarse en espacio de usuario sin\n"
    "     privilegios de Administrador para descartar cualquier manipulación a nivel de kernel.\n"
    "========================================================================================\n"
)
