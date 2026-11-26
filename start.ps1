$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$stableScript = Join-Path $repositoryRoot "backend\scripts\start-stable-flask.ps1"

Start-Process powershell.exe -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-File", $stableScript)

Write-Host "Talca Personas estable se está iniciando." -ForegroundColor Green
Write-Host "Abrí http://127.0.0.1:5000 cuando la terminal indique que está disponible."
