@echo off
REM ApexRev Test Suite Launcher
set PYTHONPATH=src
uv run python -m tests.test_engine
pause
