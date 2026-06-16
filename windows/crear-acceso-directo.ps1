# ─────────────────────────────────────────────────────────────────────
#  Crea el acceso directo "Asesor de Inversion IA" en el Escritorio
#  Ejecutar UNA VEZ desde la carpeta del proyecto:
#
#    cd C:\ruta\al\Claude-Escritorio\windows
#    PowerShell -ExecutionPolicy Bypass -File crear-acceso-directo.ps1
# ─────────────────────────────────────────────────────────────────────

# Ruta del proyecto (carpeta padre de este script)
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir  = Split-Path -Parent $ScriptDir
$BatFile     = Join-Path $ScriptDir "Asesor-Inversion.bat"

# También copiar el .bat a la raíz para facilitar el acceso
$BatRoot     = Join-Path $ProjectDir "Asesor-Inversion.bat"
if (-not (Test-Path $BatRoot)) {
    Copy-Item $BatFile $BatRoot
}

# Escritorio del usuario
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = Join-Path $Desktop "Asesor de Inversion IA.lnk"

Write-Host ""
Write-Host "  Creando acceso directo en: $Shortcut" -ForegroundColor Cyan

# Crear el .lnk usando WScript.Shell
$WshShell = New-Object -ComObject WScript.Shell
$Lnk = $WshShell.CreateShortcut($Shortcut)

$Lnk.TargetPath       = $BatRoot
$Lnk.WorkingDirectory = $ProjectDir
$Lnk.Description      = "Asesor de Inversion IA - Trading Bot"
$Lnk.WindowStyle      = 1   # ventana normal

# Intentar usar el icono del proyecto (requiere .ico en Windows)
$IcoPath = Join-Path $ProjectDir "assets\advisor-icon.ico"
if (Test-Path $IcoPath) {
    $Lnk.IconLocation = $IcoPath
} else {
    # Usar icono de Python como fallback
    $PyExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    if ($PyExe) { $Lnk.IconLocation = "$PyExe,0" }
}

$Lnk.Save()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($WshShell) | Out-Null

if (Test-Path $Shortcut) {
    Write-Host ""
    Write-Host "  Acceso directo creado correctamente." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Haz DOBLE CLIC en el icono del Escritorio:" -ForegroundColor Yellow
    Write-Host "  'Asesor de Inversion IA'" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "  ERROR: No se pudo crear el acceso directo." -ForegroundColor Red
}

Write-Host "  Pulsa Enter para cerrar..."
Read-Host
