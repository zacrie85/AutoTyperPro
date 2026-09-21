@echo off
title Auto Typer Pro - Build EXE
echo ==================================================
echo   MEMBUAT FILE .EXE DARI AUTO TYPER PRO
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

echo [1/2] Memasang pynput dan PyInstaller...
python -m pip install --upgrade pynput pyinstaller
echo.
echo [2/2] Membangun AutoTyperPro.exe (mohon tunggu 1-3 menit)...
python -m PyInstaller --onefile --windowed --name "AutoTyperPro" "%~dp0auto_typer.py"
echo.
if exist "%~dp0dist\AutoTyperPro.exe" (
    echo ==================================================
    echo   BERHASIL!
    echo   File .exe ada di:  dist\AutoTyperPro.exe
    echo ==================================================
    explorer "%~dp0dist"
) else (
    echo Gagal membuat .exe. Silakan baca pesan error di atas.
)
echo.
pause
