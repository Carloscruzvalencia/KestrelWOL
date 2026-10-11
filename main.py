"""
Punto de Entrada Principal (main.py)
KestrelWOL - Arquitectura Desacoplada Offline-First
"""

import sys
import os
from services.system_service import SystemService
from ui.app import WakeOnLanApp

# Reconfigurar codificación de consola para compatibilidad con Windows cp1252 / UTF-8
if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.stderr is not None:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def log(msg: str) -> None:
    """Imprime mensajes de diagnóstico seguros en terminal si existe salida estándar."""
    if sys.stdout is not None:
        try:
            print(msg, flush=True)
        except Exception:
            pass


def main():
    app_instance = None

    def on_restore_signal():
        if app_instance is not None:
            app_instance.bring_to_front()

    log("[*] Comprobando instancia de la aplicacion...")
    is_first_instance, lock_socket = SystemService.setup_single_instance(
        on_restore_callback=on_restore_signal
    )

    if not is_first_instance:
        log("[i] La aplicacion ya esta en ejecucion en segundo plano.")
        log("[i] Se ha enviado la senal para traer la ventana al frente.")
        sys.exit(0)

    try:
        log("[+] Cargando entorno grafico y servicios...")
        app_instance = WakeOnLanApp()
        app_instance.deiconify()
        app_instance.state("normal")
        app_instance.lift()
        app_instance.focus_force()
        log("[OK] Wake On LAN Controller iniciado correctamente.")
        app_instance.mainloop()
    except Exception as e:
        import traceback
        err_msg = f"[!] Error critico durante la ejecucion: {e}"
        if sys.stderr is not None:
            try:
                print(err_msg, file=sys.stderr, flush=True)
                traceback.print_exc()
            except Exception:
                pass
        sys.exit(1)
    finally:
        if lock_socket:
            try:
                lock_socket.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
