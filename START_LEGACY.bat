@echo off
echo ==========================================
echo Pokemon Dataset Generator - GUI Tkinter (legacy)
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run INSTALL.bat first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
set PYTHONFAULTHANDLER=1
set PYTHONIOENCODING=utf-8

python GUI_v3.1_modern.py

if %ERRORLEVEL% NEQ 0 pause
