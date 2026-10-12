# ApexRev Test Suite Launcher
Write-Host "🧪 Running ApexRev Test Suite..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"

if (Get-Command "uv" -ErrorAction SilentlyContinue) {
    & uv run python -m tests.test_engine
    exit $LASTEXITCODE
} elseif (Test-Path "$env:USERPROFILE\.local\bin\uv.exe") {
    & "$env:USERPROFILE\.local\bin\uv.exe" run python -m tests.test_engine
    exit $LASTEXITCODE
} elseif (Test-Path "$env:USERPROFILE\.local\bin\python3.14.exe") {
    & "$env:USERPROFILE\.local\bin\python3.14.exe" -m tests.test_engine
    exit $LASTEXITCODE
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    & python -m tests.test_engine
    exit $LASTEXITCODE
} else {
    Write-Error "No Python runtime found."
}
