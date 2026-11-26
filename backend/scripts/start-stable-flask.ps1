$ErrorActionPreference = "Stop"
$repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$environmentFile = Join-Path $repositoryRoot ".env"
$legacyRoot = Join-Path $repositoryRoot "backend\legacy-flask"
$pythonExecutable = Join-Path $repositoryRoot "backend\.venv\Scripts\python.exe"

if (Test-Path -LiteralPath $environmentFile) {
    foreach ($line in Get-Content -LiteralPath $environmentFile -Encoding utf8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) { continue }
        $parts = $trimmed.Split("=", 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), "Process")
    }
}

if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    throw "No existe backend\.venv. Crealo e instalá backend\legacy-flask\requirements.txt."
}

Set-Location -LiteralPath $legacyRoot
Write-Host "Talca Personas estable (main) disponible en http://127.0.0.1:5000" -ForegroundColor Green
& $pythonExecutable app.py
