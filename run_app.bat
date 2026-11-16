@echo off
title NASA SPHEREx & Planet X Explorer Launcher
echo ======================================================================
echo          NASA SPHEREx & Planet X Explorer Launcher
echo ======================================================================
echo.

:: Check if Python is installed and working
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Python detected! Checking dependencies...
    python -m pip install -r requirements.txt --quiet
    echo.
    echo Starting FastAPI & Sky Visualizer Backend at http://localhost:8000 ...
    start "" http://localhost:8000
    python -m uvicorn api:app --reload --port 8000
) else (
    echo Python was not found in PATH or is not installed yet.
    echo Launching the standalone interactive Web Visualizer directly in your browser...
    echo.
    start "" "%~dp0static\index.html"
    echo Application opened! To enable backend API endpoints, install Python from https://www.python.org/downloads/
)

pause
