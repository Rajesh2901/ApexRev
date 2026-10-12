# ApexRev Enterprise Platform - PowerShell Launcher
Write-Host "🚀 Starting ApexRev Enterprise Platform..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"

if (Get-Command "uv" -ErrorAction SilentlyContinue) {
    & uv run python main.py
    exit $LASTEXITCODE
} elseif (Test-Path "$env:USERPROFILE\.local\bin\uv.exe") {
    & "$env:USERPROFILE\.local\bin\uv.exe" run python main.py
    exit $LASTEXITCODE
} elseif (Test-Path "$env:USERPROFILE\.local\bin\python3.14.exe") {
    & "$env:USERPROFILE\.local\bin\python3.14.exe" main.py
    exit $LASTEXITCODE
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    & python main.py
    exit $LASTEXITCODE
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    & py -3 main.py
    exit $LASTEXITCODE
} else {
    Write-Error "No Python or uv runtime found. Please install Python 3.11+."
}
