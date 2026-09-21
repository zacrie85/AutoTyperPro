@echo off
title Auto Typer Pro AHK - Portable
cd /d "%~dp0"

rem 1) Interpreter portable yang sudah dibundel di paket ini
if exist "AutoHotkey64.exe" (
    start "" "AutoHotkey64.exe" "auto_typer.ahk"
    exit /b 0
)

rem 2) AutoHotkey v2 yang terpasang dan terdaftar di PATH
where AutoHotkey64.exe >nul 2>nul
if not errorlevel 1 (
    start "" AutoHotkey64.exe "%~dp0auto_typer.ahk"
    exit /b 0
)

rem 3) AutoHotkey v2 terpasang di Program Files
if exist "%ProgramFiles%\AutoHotkey\v2\AutoHotkey64.exe" (
    start "" "%ProgramFiles%\AutoHotkey\v2\AutoHotkey64.exe" "%~dp0auto_typer.ahk"
    exit /b 0
)

echo [INFO] AutoHotkey64.exe tidak ditemukan di folder ini.
echo.
echo Paket portable ini seharusnya sudah berisi AutoHotkey64.exe.
echo Jika file tersebut hilang, download resminya di:
echo    https://www.autohotkey.com/download/ahk-v2.zip
echo Lalu ekstrak "AutoHotkey64.exe" ke folder ini dan jalankan lagi.
echo.
echo Alternatif: install AutoHotkey v2 dari https://www.autohotkey.com
echo lalu klik dua kali auto_typer.ahk secara langsung.
echo.
pause
