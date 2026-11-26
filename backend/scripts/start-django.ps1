$ErrorActionPreference = "Stop"
$repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$environmentFile = Join-Path $repositoryRoot ".env"
$backendRoot = Join-Path $repositoryRoot "backend"
$pythonExecutable = Join-Path $backendRoot ".venv\Scripts\python.exe"

if (Test-Path -LiteralPath $environmentFile) {
    foreach ($line in Get-Content -LiteralPath $environmentFile -Encoding utf8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) { continue }
        $parts = $trimmed.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
    }
}

if (-not $env:DB_HOST -or -not $env:DB_NAME -or -not $env:DB_USER) {
    throw "Faltan DB_HOST, DB_NAME o DB_USER en .env."
}

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    Write-Host "Preparando el entorno Python del backend..." -ForegroundColor Cyan
    python -m venv (Join-Path $backendRoot ".venv")
    & $pythonExecutable -m pip install --upgrade pip
    & $pythonExecutable -m pip install -r (Join-Path $backendRoot "requirements.txt")
}

Set-Location -LiteralPath $backendRoot
Write-Host "API Django Talca disponible en http://127.0.0.1:8000" -ForegroundColor Green
& $pythonExecutable manage.py runserver 127.0.0.1:8000
