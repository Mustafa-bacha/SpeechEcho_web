@echo off
REM ============================================================================
REM SpeechEcho - Automated Setup Script for Windows
REM This script automates the complete setup process for a fresh Windows system
REM Usage: setup.bat
REM ============================================================================

setlocal enabledelayedexpansion

REM Colors (using echo tricks for colored output)
set "BLUE=[34m"
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "NC=[0m"

echo.
echo ===============================================================================
echo.
echo   SpeechEcho - Automated Setup for Windows
echo.
echo ===============================================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Python 3 is not installed or not in PATH
    echo Visit: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python found (%PYTHON_VERSION%)

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Visit: https://nodejs.org/
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js found (%NODE_VERSION%)

REM Check npm
echo Checking npm installation...
npm --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: npm is not installed
    exit /b 1
)
for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm found (%NPM_VERSION%)

REM Check Git
echo Checking Git installation...
git --version >nul 2>&1
if !errorlevel! neq 0 (
    echo WARNING: Git is not installed or not in PATH
    echo You can still use the project but won't be able to use git commands
)

echo.
echo ===============================================================================
echo Step 1/4: Setting up Backend
echo ===============================================================================
echo.

if not exist "backend" (
    echo ERROR: backend directory not found
    exit /b 1
)

cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create virtual environment
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip, setuptools, wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if !errorlevel! neq 0 (
    echo WARNING: Failed to upgrade pip
)
echo [OK] pip upgraded

REM Install requirements
if exist "requirements.txt" (
    echo Installing backend dependencies...
    echo This may take 5-15 minutes depending on your internet speed...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo ERROR: Failed to install backend dependencies
        exit /b 1
    )
    echo [OK] Backend dependencies installed
) else (
    echo ERROR: requirements.txt not found
    exit /b 1
)

REM Create .env
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] Backend .env created from template
        echo WARNING: Please edit backend\.env with your settings
    )
) else (
    echo [OK] Backend .env already exists
)

REM Initialize database
echo Initializing database...
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database initialized')" 2>nul
if !errorlevel! equ 0 (
    echo [OK] Database initialized
)

cd ..

REM Setup Frontend
echo.
echo ===============================================================================
echo Step 2/4: Setting up Frontend
echo ===============================================================================
echo.

if not exist "frontend" (
    echo ERROR: frontend directory not found
    exit /b 1
)

cd frontend

REM Clear npm cache
echo Clearing npm cache...
call npm cache clean --force

REM Install dependencies
echo Installing frontend dependencies...
echo This may take 2-5 minutes...
call npm install
if !errorlevel! neq 0 (
    echo ERROR: Failed to install frontend dependencies
    exit /b 1
)
echo [OK] Frontend dependencies installed

REM Create .env.local
if not exist ".env.local" (
    if exist ".env.example" (
        copy .env.example .env.local
        echo [OK] Frontend .env.local created from template
    )
) else (
    echo [OK] Frontend .env.local already exists
)

cd ..

REM Check Chatterbox
echo.
echo ===============================================================================
echo Step 3/4: Checking Chatterbox TTS
echo ===============================================================================
echo.

if exist "chatterbox-streaming" (
    echo [OK] Chatterbox TTS directory found
    echo NOTE: Models will be downloaded automatically on first use
) else (
    echo WARNING: chatterbox-streaming directory not found (optional)
)

REM Summary
echo.
echo ===============================================================================
echo Setup Complete!
echo ===============================================================================
echo.
echo Project Structure:
echo   backend\          - FastAPI backend server
echo   frontend\         - React frontend application
echo   chatterbox-streaming\ - TTS model (optional)
echo.
echo Configuration Files:
echo   backend\.env      - Backend configuration (EDIT THIS!)
echo   frontend\.env.local - Frontend configuration
echo.
echo To start the application:
echo.
echo   Terminal 1 (Backend):
echo     cd backend
echo     venv\Scripts\activate
echo     uvicorn app.main:app --reload --port 8000
echo.
echo   Terminal 2 (Frontend):
echo     cd frontend
echo     npm run dev
echo.
echo Access the application:
echo   Frontend:   http://localhost:5173
echo   API Docs:   http://localhost:8000/api/docs
echo   ReDoc:      http://localhost:8000/api/redoc
echo.
echo Remember to:
echo   1. Edit backend\.env with your configuration
echo   2. Add API keys if needed
echo.
echo For more information, see:
echo   - SETUP.md - Complete setup guide
echo   - README.md - Project overview
echo   - MODEL_DOCUMENTATION.md - Model details
echo.
echo ===============================================================================
echo.

pause
