$ErrorActionPreference = 'Stop'
$ProjectDirectory = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectDirectory

$PythonExecutable = (Get-Command python -ErrorAction Stop).Source

& $PythonExecutable (Join-Path $ProjectDirectory 'trilay_sync.py') --apply
exit $LASTEXITCODE
