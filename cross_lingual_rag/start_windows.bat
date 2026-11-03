@echo off
setlocal enabledelayedexpansion
title English-Hindi Cross-Lingual Academic RAG Platform

echo =====================================================================
echo   English-Hindi Cross-Lingual Academic RAG Experimentation Platform
echo =====================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: 2. Resolve directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if exist "cross_lingual_rag\server.py" (
    cd /d "%SCRIPT_DIR%cross_lingual_rag"
)

:: 3. Setup Virtual Environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 4. Check & Install Dependencies
echo [*] Checking dependencies...
python -c "import fastapi, uvicorn, pypdf, sentence_transformers, deep_translator" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing required packages from requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [WARNING] Some dependencies failed to install. Continuing with available packages...
    )
)

:: 5. Setup Environment File
if not exist ".env" (
    if exist ".env.example" (
        echo [*] Initializing .env from .env.example...
        copy ".env.example" ".env" >nul
        echo [NOTICE] Created .env file. You can add your GEMINI_API_KEY inside .env or in the UI settings.
    )
)

:: 6. Launch Browser and Server
set "PORT=8000"
echo [*] Starting Cross-Lingual RAG Studio on http://127.0.0.1:%PORT%...
echo [*] Opening your default web browser...

start http://127.0.0.1:%PORT%

echo.
echo =====================================================================
echo   Server is running! Press Ctrl+C in this window to stop the backend.
echo =====================================================================
echo.

python server.py

pause

