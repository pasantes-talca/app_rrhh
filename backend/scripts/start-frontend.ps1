$ErrorActionPreference = "Stop"
$repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$frontendRoot = Join-Path $repositoryRoot "frontend"

Set-Location -LiteralPath $frontendRoot
if (-not (Test-Path -LiteralPath (Join-Path $frontendRoot "node_modules"))) {
    Write-Host "Instalando dependencias del frontend..." -ForegroundColor Cyan
    npm.cmd install
}

Write-Host "Interfaz Talca disponible en http://127.0.0.1:5173" -ForegroundColor Green
npm.cmd run dev -- --host 127.0.0.1
