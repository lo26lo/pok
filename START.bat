@echo off
echo ==========================================
echo Pokemon Dataset Generator V3.1
echo ==========================================
echo.

REM Check if .venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Optional: enable Python faulthandler for better tracebacks
set PYTHONFAULTHANDLER=1
set PYTHONIOENCODING=utf-8

echo [INFO] Starting GUI (Qt)...
echo.

echo [INFO] Verifying installed packages (pip check)...
pip check
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Detected package compatibility issues above. The GUI may fail to start.
)

REM pip check only flags inconsistencies between installed packages; it does NOT
REM detect requirements.txt entries that were simply never installed (e.g. an
REM existing .venv created before a dependency like albumentations was added).
echo [INFO] Verifying required packages are importable...
python -c "import PySide6, cv2, numpy, pandas, albumentations" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Missing dependencies detected. Installing from config\requirements.txt ...
    pip install -r config\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install missing dependencies. Run INSTALL.bat manually.
        pause
        exit /b 1
    )
)

REM Check if GUI file exists
if not exist "GUI_qt.py" (
    echo [ERROR] GUI_qt.py not found!
    pause
    exit /b 1
)

REM Run the Qt GUI (fallback: START_LEGACY.bat pour l'ancienne interface Tkinter)
python GUI_qt.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] An error occurred while running the GUI.
    echo Error code: %ERRORLEVEL%
    pause
)
