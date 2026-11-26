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

if (-not $env:TALCA_API_DATABASE_URL -and $env:DB_HOST -and $env:DB_NAME -and $env:DB_USER) {
    $encodedUser = [Uri]::EscapeDataString($env:DB_USER)
    $encodedPassword = [Uri]::EscapeDataString($env:DB_PASSWORD)
    $databasePort = if ($env:DB_PORT) { $env:DB_PORT } else { "5432" }
    $env:TALCA_API_DATABASE_URL = "postgresql+psycopg://${encodedUser}:${encodedPassword}@$($env:DB_HOST):${databasePort}/$($env:DB_NAME)"
}
if (-not $env:TALCA_API_SESSION_SECRET -and $env:SECRET_KEY) { $env:TALCA_API_SESSION_SECRET = $env:SECRET_KEY }
if (-not $env:TALCA_API_ENVIRONMENT) { $env:TALCA_API_ENVIRONMENT = "development" }
if (-not $env:TALCA_API_ALLOWED_ORIGINS) { $env:TALCA_API_ALLOWED_ORIGINS = '["http://127.0.0.1:5173","http://localhost:5173"]' }

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    python -m venv (Join-Path $backendRoot ".venv")
}
& $pythonExecutable -c "import fastapi" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Instalando temporalmente el backend FastAPI estable..." -ForegroundColor Cyan
    & $pythonExecutable -m pip install -e $backendRoot
}

Set-Location -LiteralPath $backendRoot
Write-Host "API estable disponible en http://127.0.0.1:8000" -ForegroundColor Green
& $pythonExecutable -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
