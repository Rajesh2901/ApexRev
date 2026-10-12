# ApexRev Test Suite Launcher
Write-Host "🧪 Running ApexRev Test Suite..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"
uv run python -m tests.test_engine
