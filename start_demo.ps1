$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot '.venv-baseline\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) {
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $projectPython)) {
    throw 'Create the environment using README.md first, or run python app.py with Python 3.11+.'
}
& $projectPython (Join-Path $PSScriptRoot 'app.py') @args
exit $LASTEXITCODE
