@echo off
title LianYi Material Database - Update
cls
echo.
echo ============================================================
echo    LIAN YI DESIGN - Update from GitHub
echo ============================================================
echo.

REM === GitHub repository info ===
REM After setup, replace YOUR_USERNAME with your GitHub username
set GH_USER=YOUR_USERNAME
set GH_REPO=lianyi-material-db
set GH_BRANCH=main

set DOWNLOAD_URL=https://github.com/%GH_USER%/%GH_REPO%/archive/refs/heads/%GH_BRANCH%.zip
set TEMP_ZIP=%TEMP%\lianyi_update.zip
set TEMP_DIR=%TEMP%\lianyi_update

echo Downloading latest version from GitHub...
echo.

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing}"

if not exist "%TEMP_ZIP%" (
    echo.
    echo [ERROR] Download failed.
    echo Check:
    echo   1. Internet connection
    echo   2. GitHub username in UPDATE.bat is correct
    echo   3. Repository name is "lianyi-material-db"
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
