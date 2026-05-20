@echo off
title LianYi Material Database - Update
cls
echo.
echo ============================================================
echo    LIAN YI DESIGN - Update from GitHub
echo ============================================================
echo.

REM === GitHub repository info (already set for axdgcleo-design) ===
set GH_USER=axdgcleo-design
set GH_REPO=material-lab
set GH_BRANCH=main

set DOWNLOAD_URL=https://github.com/%GH_USER%/%GH_REPO%/archive/refs/heads/%GH_BRANCH%.zip
set TEMP_ZIP=%TEMP%\lianyi_update.zip
set TEMP_DIR=%TEMP%\lianyi_update

echo Downloading latest version from GitHub...
echo   User: %GH_USER%
echo   Repo: %GH_REPO%
echo.

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing } catch { Write-Host $_.Exception.Message; exit 1 }}"

if not exist "%TEMP_ZIP%" (
    echo.
    echo [ERROR] Download failed.
    echo.
    echo Possible reasons:
    echo   1. No internet connection
    echo   2. Repository is empty (you haven't uploaded files yet)
    echo   3. Repository is private and you need authentication
    echo   4. GitHub username or repo name is wrong
    echo.
    echo Current settings:
    echo   User: %GH_USER%
    echo   Repo: %GH_REPO%
    echo.
    echo URL tested: %DOWNLOAD_URL%
    echo.
    pause
    exit /b 1
)

echo Download complete. Extracting...
echo.

if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
powershell -Command "Expand-Archive -Path '%TEMP_ZIP%' -DestinationPath '%TEMP_DIR%' -Force"

set SRC_DIR=%TEMP_DIR%\%GH_REPO%-%GH_BRANCH%

if not exist "%SRC_DIR%" (
    echo [ERROR] Extracted folder not found.
    pause
    exit /b 1
)

echo Updating files (data folder is preserved)...
echo.

cd /d "%~dp0"

if exist "%SRC_DIR%\app" (
    xcopy /E /Y /I "%SRC_DIR%\app" "app" >nul
    echo   [OK] app/ updated
)

if exist "%SRC_DIR%\START.bat" (
    copy /Y "%SRC_DIR%\START.bat" "START.bat" >nul
    echo   [OK] START.bat updated
)

if exist "%SRC_DIR%\README.txt" (
    copy /Y "%SRC_DIR%\README.txt" "README.txt" >nul
)

del "%TEMP_ZIP%" >nul 2>nul
rmdir /s /q "%TEMP_DIR%" >nul 2>nul

echo.
echo ============================================================
echo   Update complete!
echo   Your data folder is untouched.
echo   Double-click START.bat to launch.
echo ============================================================
echo.
pause
