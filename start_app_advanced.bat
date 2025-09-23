@echo off
REM Kanji Test Generator Application Startup Batch File (Advanced Version)
REM Created: 2025-01-27

setlocal enabledelayedexpansion

echo ========================================
echo Starting Kanji Test Generator App...
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
    echo Or run the following commands:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
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
    echo Virtual environment may not be configured correctly
    pause
    exit /b 1
)

REM Check application file existence
if not exist "%APP_FILE%" (
    echo Error: Application file not found: %APP_FILE%
    pause
    exit /b 1
)

REM Check and install dependencies
if exist "requirements.txt" (
    echo Checking dependencies...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo Warning: Failed to install dependencies
        echo Continuing with app startup...
    ) else (
        echo Dependency check completed
    )
) else (
    echo Warning: requirements.txt not found
    echo Skipping dependency installation
)

REM Check data directory
if not exist "data" (
    echo Creating data directory...
    mkdir data
)

REM Check logs directory
if not exist "logs" (
    echo Creating logs directory...
    mkdir logs
)

REM Set Python path
set PYTHONPATH=%APP_DIR%
echo Python path set: %PYTHONPATH%

REM Start application
echo ========================================
echo Starting application...
echo ========================================
echo Browser will open automatically
echo URL: http://%HOST%:%PORT%
echo Press Ctrl+C to stop the application
echo ========================================

REM Start Streamlit application
streamlit run "%APP_FILE%" --server.port %PORT% --server.address %HOST% --server.headless false

REM Post-application cleanup
echo ========================================
echo Application has been terminated
echo ========================================
echo Press any key to close window...
pause >nul
