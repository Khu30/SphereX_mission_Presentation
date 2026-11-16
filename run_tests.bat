@echo off
title NASA SPHEREx Benchmark Verification Runner
echo ======================================================================
echo          NASA SPHEREx Step 5 Benchmark Verification Suite
echo ======================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python test_benchmarks.py
) else (
    echo Python is required to run the automated benchmark script.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
)

echo.
pause
