@echo off
chcp 65001 >nul 2>&1
title Asesor de Inversión IA

:: ─────────────────────────────────────────────────────────────
::  Asesor de Inversión IA — Lanzador Windows
::  Detecta automáticamente: WSL, Python local
:: ─────────────────────────────────────────────────────────────

:: Directorio del proyecto (relativo al .bat)
set "BOT_DIR=%~dp0"
set "BOT_DIR=%BOT_DIR:~0,-1%"

:: Subir un nivel si estamos en la subcarpeta "windows"
for %%I in ("%BOT_DIR%") do set "PARENT=%%~dpI"
for %%I in ("%PARENT:~0,-1%") do set "FOLDER_NAME=%%~nxI"
if /i "%~nx0"=="Asesor-Inversion.bat" (
    if exist "%BOT_DIR%\main.py" (
        :: El .bat está en la raíz del proyecto
    ) else if exist "%PARENT%main.py" (
        set "BOT_DIR=%PARENT:~0,-1%"
    )
)

cls
echo.
echo   ╔═══════════════════════════════════════════════════════╗
echo   ║     🤖  Asesor de Inversión IA  —  Iniciando...      ║
echo   ╚═══════════════════════════════════════════════════════╝
echo.

:: ── Intentar WSL primero (experiencia óptima) ────────────────
where wsl >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo   Usando WSL (recomendado)...
    echo.
    :: Convertir ruta Windows a ruta WSL
    for /f "tokens=*" %%p in ('wsl wslpath -u "%BOT_DIR%"') do set "WSL_PATH=%%p"
    wsl bash -c "cd '%WSL_PATH%' && [ -f .venv/bin/activate ] && source .venv/bin/activate; python main.py advisor"
    goto :end
)

:: ── Python local ─────────────────────────────────────────────
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo   Usando Python local...
    echo.
    cd /d "%BOT_DIR%"
    :: Activar venv si existe
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    )
    python main.py advisor
    goto :end
)

where python3 >nul 2>&1
if %ERRORLEVEL% == 0 (
    cd /d "%BOT_DIR%"
    if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
    python3 main.py advisor
    goto :end
)

:: ── Sin Python ni WSL ────────────────────────────────────────
echo   ERROR: No se encontró Python ni WSL.
echo.
echo   Opciones:
echo   1. Instalar Python desde https://python.org
echo   2. Instalar WSL: abrir PowerShell como admin y ejecutar:
echo         wsl --install
echo.

:end
echo.
pause
