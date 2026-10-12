@echo off
REM ApexRev Enterprise Platform - Quick Launcher
echo =======================================================
echo Starting ApexRev Platform...
echo =======================================================
set PYTHONPATH=src

where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    uv run python main.py
    goto end
)

if exist "%USERPROFILE%\.local\bin\uv.exe" (
    "%USERPROFILE%\.local\bin\uv.exe" run python main.py
    goto end
)

if exist "%USERPROFILE%\.local\bin\python3.14.exe" (
    "%USERPROFILE%\.local\bin\python3.14.exe" main.py
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python main.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 main.py
    goto end
)

echo ERROR: No Python or uv runtime found. Please install Python 3.11+.
:end
pause
