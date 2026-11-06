@echo off
setlocal
title English-Hindi Cross-Lingual Academic RAG Platform

echo =====================================================================
echo   English-Hindi Cross-Lingual Academic RAG Experimentation Platform
echo =====================================================================
echo.

:: 1. Navigate to cross_lingual_rag directory
cd /d "%~dp0"
if exist "cross_lingual_rag\server.py" (
    cd cross_lingual_rag
)

if not exist "server.py" (
    echo [ERROR] server.py was not found in the current directory.
    echo Please ensure the project was unzipped completely before running.
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

:: 2. Find a working Python executable (python, py -3, py, python3)
set "PY_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :python_found
)

py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py -3"
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python3"
    goto :python_found
)

:python_not_found
echo [ERROR] Python is not installed or not registered in your Windows PATH.
echo.
echo Please install Python 3.10, 3.11, or 3.12 from:
echo   https://www.python.org/downloads/
echo.
echo CRITICAL STEP DURING INSTALLATION:
echo   Make sure to check the box: [X] "Add python.exe to PATH"
echo.
echo If Python is already installed, turn OFF Windows App Execution Aliases:
echo   Windows Settings -^> Apps -^> Advanced app settings -^> App execution aliases
echo   Turn OFF "App Installer (python.exe)" and "App Installer (python3.exe)"
echo.
pause
exit /b 1

:python_found
echo [*] Detected Python environment: %PY_CMD%
%PY_CMD% --version

:: 3. Check if core dependencies are already satisfied in the current environment
echo [*] Checking dependencies...
%PY_CMD% -c "import fastapi, uvicorn, pypdf, sentence_transformers, deep_translator" >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Core dependencies already verified!
    goto :check_env
)

:: 4. If dependencies not in global python, setup/activate virtual environment (.venv)
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating existing virtual environment .venv...
    call .venv\Scripts\activate.bat
    set "PY_CMD=python"
    goto :install_deps
)

echo [*] Creating local virtual environment .venv...
%PY_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [WARNING] Could not create virtual environment .venv. Continuing with %PY_CMD%...
    goto :install_deps
)

echo [*] Activating newly created .venv...
call .venv\Scripts\activate.bat
set "PY_CMD=python"

:install_deps
echo [*] Verifying packages in virtual environment...
%PY_CMD% -c "import fastapi, uvicorn, pypdf, sentence_transformers, deep_translator" >nul 2>&1
if %errorlevel% neq 0 (
    if exist "requirements.txt" (
        echo [*] Installing required packages from requirements.txt...
        echo [*] Note: Initial download of PyTorch and embedding models may take a few minutes.
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo [WARNING] Some dependencies had warnings during installation. Continuing...
        )
    )
)

:check_env
:: 5. Setup .env file if missing
if not exist ".env" (
    if exist ".env.example" (
        echo [*] Initializing .env from .env.example...
        copy ".env.example" ".env" >nul
        echo [NOTICE] Created .env configuration file.
    )
)

:: 6. Launch browser and server
set "PORT=8000"
echo.
echo =====================================================================
echo   Starting Cross-Lingual Academic RAG Studio on port %PORT%...
echo   Open in browser: http://127.0.0.1:%PORT%
echo =====================================================================
echo.

start http://127.0.0.1:%PORT%

%PY_CMD% server.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Server terminated with exit code %errorlevel%.
    echo Please review any traceback messages printed above.
    pause
)

