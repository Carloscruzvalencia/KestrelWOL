#!/usr/bin/env python3
"""
KestrelWOL - Test Suite Runner (tests/run_tests.py)
Ejecuta la suite completa de pruebas unitarias y de integración de forma rápida.
"""

import os
from pathlib import Path
import sys
import time
import unittest

if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    # Asegurar que el directorio raíz del proyecto esté en sys.path
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    print("=" * 70)
    print(" 🦅 KESTRELWOL TEST SUITE - FAST VERIFICATION RUNNER")
    print("=" * 70)

    start_time = time.time()

    # Descubrir y cargar todos los tests dentro del paquete 'tests'
    tests_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir), pattern="test_*.py")

    # Ejecutar con runner verbal
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    elapsed = time.time() - start_time

    print("=" * 70)
    print(f" Tests ejecutados: {result.testsRun}")
    print(f" Éxitos:           {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Fallos:           {len(result.failures)}")
    print(f" Errores:          {len(result.errors)}")
    print(f" Tiempo total:     {elapsed:.3f} segundos")
    print("=" * 70)

    if result.wasSuccessful():
        print(" [OK] Todos los componentes han pasado las pruebas satisfactoriamente.")
        sys.exit(0)
    else:
        print(" [ERROR] Se han detectado fallos en las pruebas.")
        sys.exit(1)


if __name__ == "__main__":
    main()
