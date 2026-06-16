# ─────────────────────────────────────────────────────────────────────
#  Crea el acceso directo "Asesor de Inversion IA" en el Escritorio
#  Compatible con PowerShell 5 y PowerShell 7 (Windows).
#
#  Ejecutar desde CUALQUIER carpeta del proyecto:
#    PowerShell -ExecutionPolicy Bypass -File crear-acceso-directo.ps1
# ─────────────────────────────────────────────────────────────────────

# Detectar la ruta de este script aunque se llame desde otro directorio
$ScriptDir  = Split-Path -Parent (Resolve-Path $MyInvocation.MyCommand.Path)
$ProjectDir = Split-Path -Parent $ScriptDir
$BatFile    = Join-Path $ScriptDir "Asesor-Inversion.bat"

# Copiar el .bat a la raíz del proyecto para que el acceso directo lo encuentre
$BatRoot = Join-Path $ProjectDir "Asesor-Inversion.bat"
if (-not (Test-Path $BatRoot)) {
    Copy-Item $BatFile $BatRoot
}

# Escritorio del usuario actual
$Desktop  = [Environment]::GetFolderPath("Desktop")
$Shortcut = Join-Path $Desktop "Asesor de Inversion IA.lnk"

Write-Host ""
Write-Host "  Proyecto : $ProjectDir" -ForegroundColor DarkGray
Write-Host "  Creando  : $Shortcut"  -ForegroundColor Cyan

# Crear el .lnk con WScript.Shell (PowerShell 5 compatible)
$WshShell             = New-Object -ComObject WScript.Shell
$Lnk                  = $WshShell.CreateShortcut($Shortcut)
$Lnk.TargetPath       = $BatRoot
$Lnk.WorkingDirectory = $ProjectDir
$Lnk.Description      = "Asesor de Inversion IA - Trading Bot"
$Lnk.WindowStyle      = 1

# Icono: usar .ico del proyecto si existe, si no el de Python
$IcoPath = Join-Path $ProjectDir "assets\advisor-icon.ico"
if (Test-Path $IcoPath) {
    $Lnk.IconLocation = $IcoPath
} else {
    $PyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($PyCmd -ne $null) {
        $Lnk.IconLocation = $PyCmd.Source + ",0"
    }
}

$Lnk.Save()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($WshShell) | Out-Null

if (Test-Path $Shortcut) {
    Write-Host ""
    Write-Host "  Acceso directo creado correctamente." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Ve al Escritorio y haz DOBLE CLIC en:" -ForegroundColor Yellow
    Write-Host "  Asesor de Inversion IA" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "  ERROR: No se pudo crear el acceso directo." -ForegroundColor Red
    Write-Host "  Intenta ejecutar PowerShell como Administrador." -ForegroundColor Red
}

Write-Host "  Pulsa Enter para cerrar..."
Read-Host
