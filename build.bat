@echo off
setlocal
set PY=C:\Users\Rohith\AppData\Local\Python\pythoncore-3.12-64\python.exe
set INNO="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

echo ============================================================
echo  School Uniform Billing -- Build Script
echo ============================================================
echo.

:: Step 1 — Install / upgrade PyInstaller
echo [1/4] Installing PyInstaller...
%PY% -m pip install --quiet --upgrade pyinstaller
if errorlevel 1 ( echo FAILED & pause & exit /b 1 )

:: Step 2 — Clean previous build artefacts
echo [2/4] Cleaning previous build...
if exist build       rmdir /s /q build
if exist dist        rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output

:: Step 3 — PyInstaller: bundle into dist\UniformBilling\
echo [3/4] Running PyInstaller...
%PY% -m PyInstaller build.spec --noconfirm
if errorlevel 1 ( echo PyInstaller FAILED & pause & exit /b 1 )
echo PyInstaller done. Folder: dist\UniformBilling\

:: Step 4 — Inno Setup: produce installer EXE
echo [4/4] Running Inno Setup...
if not exist %INNO% (
    echo Inno Setup not found at %INNO%
    echo Download from https://jrsoftware.org/isdl.php and install, then re-run.
    pause & exit /b 1
)
%INNO% installer.iss
if errorlevel 1 ( echo Inno Setup FAILED & pause & exit /b 1 )

echo.
echo ============================================================
echo  SUCCESS!
echo  Installer: installer_output\UniformBilling_Setup_v1.0.0.exe
echo ============================================================
pause
