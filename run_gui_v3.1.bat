@echo off
echo ==========================================
echo Pokemon Dataset Generator V3.1
echo ==========================================
echo.

REM Check if .venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run install_env.bat first.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Starting GUI v3.1...
echo.

REM Check if GUI file exists
if not exist "GUI_v3.1_modern.py" (
    echo [ERROR] GUI_v3.1_modern.py not found!
    pause
    exit /b 1
)

REM Run the GUI
python GUI_v3.1_modern.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An error occurred while running the GUI.
    echo Error code: %ERRORLEVEL%
    pause
)
