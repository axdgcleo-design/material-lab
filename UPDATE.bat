@echo off
title LianYi Material Database - Update
cls
echo.
echo ============================================================
echo    LIAN YI DESIGN - Update from GitHub
echo ============================================================
echo.

set GH_USER=axdgcleo-design
set GH_REPO=material-lab
set GH_BRANCH=main

set DOWNLOAD_URL=https://github.com/%GH_USER%/%GH_REPO%/archive/refs/heads/%GH_BRANCH%.zip
set TEMP_ZIP=%TEMP%\lianyi_update.zip
set TEMP_DIR=%TEMP%\lianyi_update

echo Downloading from GitHub...
echo   %DOWNLOAD_URL%
echo.

if exist "%TEMP_ZIP%" del /f /q "%TEMP_ZIP%"

REM Try curl with SSL revocation check disabled (common in corporate networks)
where curl >nul 2>nul
if not errorlevel 1 (
    echo Using curl with relaxed SSL settings...
    curl -L --ssl-no-revoke -o "%TEMP_ZIP%" "%DOWNLOAD_URL%"
    if exist "%TEMP_ZIP%" goto check_size
)

REM Fallback to PowerShell with relaxed SSL
echo Trying PowerShell as fallback...
powershell -ExecutionPolicy Bypass -Command "& { [System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%TEMP_ZIP%' -UseBasicParsing -ErrorAction Stop } catch { Write-Host ('Error: ' + $_.Exception.Message); exit 1 }}"

:check_size
if not exist "%TEMP_ZIP%" goto download_failed

for %%A in ("%TEMP_ZIP%") do set FSIZE=%%~zA
if %FSIZE% LSS 1000 (
    echo.
    echo [WARNING] Downloaded file is suspiciously small: %FSIZE% bytes
    del /f /q "%TEMP_ZIP%"
    goto download_failed
)

echo Download OK (%FSIZE% bytes). Extracting...
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

del /f /q "%TEMP_ZIP%" >nul 2>nul
rmdir /s /q "%TEMP_DIR%" >nul 2>nul

echo.
echo ============================================================
echo   Update complete!
echo   Your data folder is untouched.
echo   Double-click START.bat to launch.
echo ============================================================
echo.
pause
exit /b 0

:download_failed
echo.
echo [ERROR] Download failed.
echo.
echo If you see SSL certificate errors:
echo   - This is usually a corporate network or VPN issue
echo   - The script tried both curl and PowerShell
echo.
echo Manual workaround:
echo   1. Open browser, go to:
echo      %DOWNLOAD_URL%
echo   2. Save the zip file
echo   3. Extract and copy app/ START.bat README.txt over the old ones
echo.
pause
exit /b 1
