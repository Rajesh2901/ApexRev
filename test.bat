@echo off
REM ApexRev Test Suite Launcher
set PYTHONPATH=src

where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    uv run python -m tests.test_engine
    goto end
)

if exist "%USERPROFILE%\.local\bin\uv.exe" (
    "%USERPROFILE%\.local\bin\uv.exe" run python -m tests.test_engine
    goto end
)

if exist "%USERPROFILE%\.local\bin\python3.14.exe" (
    "%USERPROFILE%\.local\bin\python3.14.exe" -m tests.test_engine
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python -m tests.test_engine
    goto end
)

echo ERROR: No Python runtime found.
:end
pause
