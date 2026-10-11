<div align="center">

<img src="assets/logo-banner.png" alt="KestrelWOL Banner" width="720" />

# KestrelWOL
### Industrial Remote Power, Network Fleet Management & Subnet Automation

[![Python](https://img.shields.io/badge/Python-3.10_%7C_3.11_%7C_3.12-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-10_%7C_11_%7C_Server-0078d4?logo=windows&logoColor=white)](https://microsoft.com)
[![CPU](https://img.shields.io/badge/CPU-x64_%7C_ARM64-f97316?logo=intel&logoColor=white)](#)
[![Protocol](https://img.shields.io/badge/Protocol-Wake--on--LAN-0284c7?logo=wireshark&logoColor=white)](#)
[![Audit](https://img.shields.io/badge/Audit-SHA--256_Chained-10b981?logo=letsencrypt&logoColor=white)](#)
[![License](https://img.shields.io/badge/License-MIT-0284c7?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Cost](https://img.shields.io/badge/Cost-Free_and_Open_Source-22c55e?logo=github&logoColor=white)](LICENSE)

<br/>

> **KestrelWOL** es una plataforma moderna, industrial y estricta para el control de energía remoto, encendido masivo programado (Wake-on-LAN) y telemetría de flotas informáticas en redes corporativas sin conexión a Internet (*Air-Gapped / Offline-First*).

</div>

---

## 📊 Comparativa de Características (Features)

| Funcionalidad / Aspecto Clave | 🦅 KestrelWOL | ◽ Otras herramientas WOL genéricas |
| :--- | :---: | :---: |
| **Protección eléctrica escalonada (anti inrush-current 250ms)** | ✔️ | ❌ |
| **Auditoría forense inmutable con SHA-256 encadenado** | ✔️ | ❌ |
| **Acceso directo en 1-clic a RDP (`mstsc`) y consola SSH** | ✔️ | ❌ |
| **Apagado y reinicio remoto controlado con aviso (30s)** | ✔️ | ❌ |
| **Programador semanal desatendido con System Tray** | ✔️ | 〰️ |
| **Agrupación y filtrado inteligente por zonas** | ✔️ | ❌ |
| **Importación/Exportación CSV segura (anti-fórmulas)** | ✔️ | ❌ |

---

## 💻 Instalación y Uso Rápido

### Requisitos del Sistema
- **Sistema Operativo**: Windows 10, Windows 11 o Windows Server (x64 / ARM64).
- **Entorno de Ejecución**: Python 3.10 o superior (el lanzador lo instala automáticamente si falta).

### 🚀 Lanzamiento en 1 Clic (Recomendado)
Haz doble clic en el archivo **`run.bat`**. Comprobará las dependencias necesarias e iniciará la interfaz gráfica directamente.

```cmd
# Lanzamiento directo desde CMD o PowerShell:
run.bat
```

### 📦 Ejecución Manual
```bash
# 1. Clonar o descargar el repositorio
cd WakeOnLanResetXr-main

# 2. Instalar dependencias en el entorno
pip install -r requirements.txt

# 3. Iniciar la aplicación
python main.py
```

> **Consejo para entornos sin consola**: Puedes iniciar el lanzador silencioso de Windows haciendo doble clic en **`gui.pyw`** para ocultar cualquier ventana de terminal en segundo plano.

---

## ⌨️ Utilidad de Línea de Comandos (CLI Headless)

KestrelWOL incluye una CLI desacoplada ideal para scripts de mantenimiento programado en el Programador de Tareas de Windows (*Task Scheduler*):

```bash
# Encender todos los equipos registrados con protección anti-inrush
python cli.py --all

# Encender únicamente los puestos pertenecientes a una sala o zona
python cli.py --zone "Oficina A"

# Ajustar el retardo eléctrico escalonado (ejemplo: 0.5 segundos)
python cli.py --all --delay 0.50

# Listar el inventario de dispositivos en terminal
python cli.py --list

# Escanear puertos y servicios abiertos en un host (RDP, SSH, WEB, VNC)
python cli.py --check-services 192.168.1.50

# Ordenar un apagado o reinicio preventivo remoto (30s)
python cli.py --shutdown 192.168.1.50
python cli.py --reboot 192.168.1.50

# Exportar o importar masivamente la base de datos a CSV
python cli.py --export-csv "inventario.csv"
python cli.py --import-csv "inventario.csv"
```

---

## 💬 Contacto

Para consultas generales, propuestas de mejora o reportes de seguridad relacionados con **KestrelWOL**, puedes comunicarte directamente a través de:

- **Consultas generales y soporte**: [a2carcruzinfo@gmail.com](mailto:a2carcruzinfo@gmail.com)
- **Reportes de vulnerabilidades y seguridad**: [a2carcruzinfo@gmail.com](mailto:a2carcruzinfo@gmail.com)

---

## 📜 Licencia y Atribución

Este proyecto es software libre y de código abierto bajo los términos de la **Licencia MIT**. Puedes consultar el texto íntegro en el archivo [LICENSE](LICENSE).

> **Aviso**: Cualquier redistribución o uso de este código debe preservar el aviso de copyright original y la atribución a los autores del proyecto.
