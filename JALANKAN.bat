@echo off
title Auto Typer Pro - Jalankan Cepat
echo ==================================================
echo   AUTO TYPER PRO - Menjalankan aplikasi...
echo ==================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python belum terpasang di komputer ini.
    echo.
    echo   1. Download Python gratis di:  https://www.python.org/downloads/
    echo   2. Saat instalasi, CENTANG pilihan "Add Python to PATH"
    echo   3. Setelah terpasang, klik dua kali file ini lagi.
    echo.
    pause
    exit /b 1
)

echo Memastikan library pynput terpasang...
python -m pip install --quiet pynput
echo.
echo Memulai Auto Typer Pro...
python "%~dp0auto_typer.py"
if errorlevel 1 (
    echo.
    echo Terjadi kesalahan saat menjalankan aplikasi.
    pause
)
