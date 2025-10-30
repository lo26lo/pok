@echo off
REM install_env.bat
REM Creates a virtual environment in .venv, activates it and installs dependencies.
REM Forces Python 3.12 for NumPy wheel compatibility (Python 3.13 lacks pre-built wheels)
SETLOCAL
cd /d "%~dp0"

:: Try to find Python 3.12 first (recommended for NumPy compatibility)
echo Searching for Python 3.12 (recommended for pre-compiled NumPy wheels)...
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    py -3.12 --version >nul 2>&1
    if %ERRORLEVEL%==0 (
        set PYEXEC=py -3.12
        echo Found Python 3.12 via py launcher
        goto :found_python
    )
)

:: Fallback to any Python 3.x
echo Python 3.12 not found, trying any Python 3.x...
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set PYEXEC=py -3
    echo WARNING: Using latest Python version - may require C++ compiler for NumPy
) else (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        set PYEXEC=python
        echo WARNING: Using 'python' command - may require C++ compiler for NumPy
    ) else (
        where python3 >nul 2>&1
        if %ERRORLEVEL%==0 (
            set PYEXEC=python3
            echo WARNING: Using 'python3' command - may require C++ compiler for NumPy
        ) else (
            echo ERROR: No python launcher found in PATH.
            echo Please install Python 3.12 from https://www.python.org/downloads/
            pause
            exit /b 1
        )
    )
)

:found_python
echo Using Python: %PYEXEC%
%PYEXEC% -V

:: Check if .venv exists with wrong Python version
if exist ".venv\Scripts\python.exe" (
    echo Checking existing virtual environment...
    .venv\Scripts\python.exe --version 2>nul | findstr /C:"3.13" >nul
    if %ERRORLEVEL%==0 (
        echo WARNING: Existing .venv uses Python 3.13 which lacks NumPy wheels
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
call .venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel

:: Install core dependencies from requirements.txt
echo Installing dependencies from requirements.txt (this may take several minutes)...
echo This will install NumPy ^<2.0 for imgaug compatibility...
if exist requirements.txt (
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Failed to install dependencies from requirements.txt
        echo.
        echo If you see "Unknown compiler" errors, you have two options:
        echo   1. Install Python 3.12 instead of 3.13: https://www.python.org/downloads/release/python-3120/
        echo   2. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
        echo.
        echo Recommended: Delete .venv folder and re-run with Python 3.12
        pause
        exit /b 1
    )
) else (
    echo WARNING: requirements.txt not found, installing packages manually...
    REM Core deps for Pokemons scripts - NumPy pinned to <2.0 for imgaug compatibility
    pip install "numpy<2.0" pandas opencv-python pillow requests scipy scikit-image imgaug imagecorruptions openpyxl
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

:: Create a helper to run GUI using the venv interpreter
echo @echo off > run_with_env.bat
echo cd /d "%~dp0" >> run_with_env.bat
echo call .venv\Scripts\activate >> run_with_env.bat
echo python GUI.py %%* >> run_with_env.bat
echo pause >> run_with_env.bat

echo Created run_with_env.bat (use it to launch the GUI with the venv)
echo To activate the venv now use: call .venv\Scripts\activate
pause
ENDLOCAL
