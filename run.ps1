# ApexRev Enterprise Platform - PowerShell Launcher
Write-Host "🚀 Starting ApexRev Platform..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"
uv run python main.py
