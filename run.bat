@echo off
setlocal
title KestrelWOL
 
:: Cambiar al directorio local del script
cd /d "%~dp0"
 
echo ===================================================
echo   KestrelWOL - Launcher
echo ===================================================

echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed. Attempting to install via Winget...
    winget install -e --id Python.Python.3.12 --scope machine
    if %errorlevel% neq 0 (
        echo [x] Failed to install Python automatically.
        echo     Please install Python 3.10+ manually from https://python.org
        pause
        exit /b 1
    )
    echo [+] Python installed successfully. Please re-run this script.
    pause
    exit /b 0
)

echo [*] Verifying dependencies...
python -c "import wakeonlan, pystray, PIL, customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
) else (
    echo [+] All dependencies are satisfied.
)

echo [*] Starting KestrelWOL...
powershell -Command "Get-NetTCPConnection -LocalPort 47829,47830 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
powershell -Command "Stop-Process -Name 'pythonw*' -Force -ErrorAction SilentlyContinue" >nul 2>&1
start "" pythonw "%~dp0main.py"
exit /b 0
