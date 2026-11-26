$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendScript = Join-Path $repositoryRoot "backend\scripts\start-django.ps1"
$frontendScript = Join-Path $repositoryRoot "backend\scripts\start-frontend.ps1"

Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $backendScript)
Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $frontendScript)

Write-Host "La arquitectura Django de Talca Personas se está iniciando en dos terminales." -ForegroundColor Green
Write-Host "Este arranque es de migración; usá start.ps1 para la versión funcional estable."
