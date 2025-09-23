@echo off
REM Kanji Test Generator Application Startup Batch File
REM Created: 2025-01-27

echo ========================================
echo Starting Kanji Test Generator App...
echo ========================================

REM Get current directory
set "CURRENT_DIR=%~dp0"
echo Working Directory: %CURRENT_DIR%

REM Change to working directory
cd /d "%CURRENT_DIR%"
if %errorlevel% neq 0 (
    echo Error: Failed to change working directory
    pause
    exit /b 1
)

REM Check virtual environment existence
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please create virtual environment: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check Python existence
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Virtual environment may not be configured correctly
    pause
    exit /b 1
)

REM Check dependencies
if not exist "requirements.txt" (
    echo Warning: requirements.txt not found
    echo Skipping dependency installation
) else (
    echo Checking dependencies...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo Warning: Failed to install dependencies
        echo Continuing with app startup...
    )
)

REM Set Python path
set PYTHONPATH=%CURRENT_DIR%
echo Python path set: %PYTHONPATH%

REM Start application
echo ========================================
echo Starting application...
echo ========================================
echo Browser will open automatically
echo Press Ctrl+C to stop the application
echo ========================================

REM Start Streamlit application
streamlit run src/app.py --server.port 8501 --server.address localhost

REM Post-application cleanup
echo ========================================
echo Application has been terminated
echo ========================================
pause
