@echo off
REM install_env.bat
REM Creates a virtual environment in .venv, activates it and installs dependencies.
REM Forces Python 3.12 for NumPy wheel compatibility (Python 3.13 lacks pre-built wheels)
SETLOCAL

:: Try to find a compatible Python (prefer 3.12, then 3.11/3.10)
echo Searching for a compatible Python (3.12 preferred for NumPy wheels)...
set "PYEXEC="

where py >nul 2>&1 && (
    for %%V in (3.12 3.11 3.10) do (
        py -%%V --version >nul 2>&1 && (
            set "PYEXEC=py -%%V"
            echo Found Python %%V via py launcher
            goto :found_python
        )
    )
)

:: If py is present but no compatible 3.12/3.11/3.10 was found, do NOT fall back to 3.13+ (NumPy wheels often unavailable)
where py >nul 2>&1 && (
    echo ERROR: No compatible Python (3.10/3.11/3.12) found by the py launcher.
    echo        Detected versions may be too new (e.g., 3.13+), which lack pre-built NumPy wheels.
    echo.
    echo Please install Python 3.12 (recommended) with one of the options below:
    echo   - Microsoft Store: https://apps.microsoft.com/detail/9NCVDN91XZQP
    echo   - Winget: winget install --id Python.Python.3.12 -e
    echo   - Official site: https://www.python.org/downloads/release/python-3120/
    echo.
    echo After installing, re-run install_env.bat
    pause
    exit /b 1
)

:: Fallback to direct python/python3 commands if py launcher is missing
where py >nul 2>&1 || (
    where python >nul 2>&1 && (
        set "PYEXEC=python"
        goto :found_python
    )
    where python3 >nul 2>&1 && (
        set "PYEXEC=python3"
        goto :found_python
    )
    echo ERROR: No Python found in PATH.
    echo Please install Python 3.12 from https://www.python.org/downloads/
    pause
    exit /b 1
)

:found_python
echo Using Python: %PYEXEC%
%PYEXEC% -V

:: Check if .venv exists with wrong Python version
if exist ".venv\Scripts\python.exe" (
    echo Checking existing virtual environment...
    .venv\Scripts\python.exe --version 2>nul | findstr "3.13 3.14" >nul
    if %ERRORLEVEL%==0 (
        echo WARNING: Existing .venv uses Python 3.13+ which lacks NumPy 1.x wheels
        echo Removing old .venv to recreate with compatible Python version...
        rmdir /s /q .venv
    )
)

:: Create virtual environment in .venv if missing
if not exist ".venv\Scripts\activate" (
    echo Creating virtual environment in .venv ...
    %PYEXEC% -m venv .venv || (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists at .venv
)

:: Activate venv and upgrade pip
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel

:: Install dependencies (prefer pre-built wheels for heavy packages to avoid compilation)
echo Installing dependencies (favoring pre-built wheels for speed)...
echo NumPy 2.x supporte (Albumentations) ; PySide6 pour l'interface Qt.

REM Step 1: Pre-install heavy binary packages with wheels-only where possible
REM PySide6 est volumineux et TOUJOURS distribue en wheel : on le met ici.
echo.
echo [1/2] Installing heavy packages from wheels (no compilation):
pip install --only-binary=:all: "numpy>=1.24" "opencv-python>=4.8.0" "scipy>=1.11" "scikit-image>=0.21" "pyside6>=6.5"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Some heavy packages could not be installed from wheels only.^>
    echo          Falling back to normal installation in the next step.
)

REM Step 2: Install remaining requirements normally (will skip already satisfied packages)
echo.
echo [2/2] Installing remaining requirements from requirements.txt ...
if exist config\requirements.txt (
    pip install -r config\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install dependencies from requirements.txt
        echo.
        echo If you see "Unknown compiler" errors, you have two options:
        echo   1. Install Python 3.12 (recommended): https://www.python.org/downloads/release/python-3120/
        echo   2. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
        echo.
        echo Recommended: Delete .venv folder and re-run with Python 3.12
        pause
        exit /b 1
    )
) else (
    echo WARNING: config\requirements.txt not found, installing core packages manually...
    pip install "numpy>=1.24" pandas "opencv-python>=4.8.0" pillow requests scipy scikit-image "albumentations>=1.3.0,<2.0" imagecorruptions openpyxl pyside6
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Manual installation failed. See error message above.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================

:: Create a helper to run GUI using the venv interpreter (interface Qt)
echo @echo off > run_with_env.bat
echo cd /d "%~dp0" >> run_with_env.bat
echo call .venv\Scripts\activate.bat >> run_with_env.bat
echo python GUI_qt.py %%* >> run_with_env.bat
echo pause >> run_with_env.bat

echo Created run_with_env.bat (use it to launch the Qt GUI with the venv)
echo Or simply use START.bat after installation (START_LEGACY.bat for Tkinter)
echo To activate the venv now use: call .venv\Scripts\activate.bat
pause
ENDLOCAL
