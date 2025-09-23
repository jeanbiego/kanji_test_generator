@echo off
REM Kanji Test Generator Application Startup Batch File (Development Mode)
REM Created: 2025-01-27

setlocal enabledelayedexpansion

echo ========================================
echo Starting Kanji Test Generator App (Development Mode)
echo ========================================

REM Configuration variables
set "APP_DIR=%~dp0"
set "VENV_DIR=%APP_DIR%venv"
set "APP_FILE=%APP_DIR%src\app.py"
set "PORT=8501"
set "HOST=localhost"

REM Change to working directory
echo Working Directory: %APP_DIR%
cd /d "%APP_DIR%"
if %errorlevel% neq 0 (
    echo Error: Failed to change working directory
    pause
    exit /b 1
)

REM Check virtual environment existence
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please create virtual environment: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check Python existence
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    pause
    exit /b 1
)

REM Install development dependencies
if exist "requirements.txt" (
    echo Installing development dependencies...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo Warning: Failed to install dependencies
    )
)

REM Install development tools (optional)
echo Checking development tools...
pip install black ruff mypy pytest --quiet >nul 2>&1

REM Run code formatting (optional)
echo Running code formatting...
black src/ --quiet >nul 2>&1
ruff check src/ --fix --quiet >nul 2>&1

REM Set Python path
set PYTHONPATH=%APP_DIR%
echo Python path set: %PYTHONPATH%

REM Start application
echo ========================================
echo Starting application (Development Mode)...
echo ========================================
echo Browser will open automatically
echo URL: http://%HOST%:%PORT%
echo Press Ctrl+C to stop the application
echo ========================================

REM Start Streamlit application (Development Mode)
streamlit run "%APP_FILE%" --server.port %PORT% --server.address %HOST% --server.headless false --server.runOnSave true

REM Post-application cleanup
echo ========================================
echo Application has been terminated
echo ========================================
pause
