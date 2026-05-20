@echo off
title LianYi Material Database
cls
echo.
echo ============================================================
echo    LIAN YI DESIGN - Material Database  v0.3
echo ============================================================
echo.

set PYTHON_CMD=

python --version >nul 2>nul
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto found_python
)

python3 --version >nul 2>nul
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto found_python
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    goto found_python
)

echo [ERROR] Python Not Found
echo.
echo Please install Python first:
echo.
echo   Option A: Microsoft Store
echo     1. Open Microsoft Store
echo     2. Search "Python 3.12"
echo     3. Install
echo.
echo   Option B: Official Website
echo     1. Visit https://www.python.org/downloads/
echo     2. Download and run installer
echo     3. CHECK "Add python.exe to PATH"
echo     4. Click Install Now
echo.
echo ============================================================
pause
exit /b 1

:found_python
echo [OK] Found Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

%PYTHON_CMD% -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo First time setup: installing Flask...
    echo.
    %PYTHON_CMD% -m pip install flask --quiet
    if errorlevel 1 (
        echo.
        echo [ERROR] Flask installation failed.
        echo Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
    echo [OK] Flask installed
    echo.
)

cd /d "%~dp0"
echo ============================================================
echo   Starting server... Browser will open automatically
echo.
echo   *** DO NOT close this window while using the app ***
echo ============================================================
echo.

%PYTHON_CMD% app\server.py

echo.
echo ============================================================
echo   Server stopped
echo ============================================================
pause
