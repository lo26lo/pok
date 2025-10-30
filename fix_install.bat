@echo off
REM fix_install.bat - Quick fix to install dependencies in existing .venv
cd /d "%~dp0"

if not exist ".venv\Scripts\activate" (
    echo ERROR: .venv not found. Run install_env.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Installing dependencies (this will take several minutes)...
echo.

REM Install packages one by one with error checking
echo [1/10] Installing numpy...
pip install "numpy<2.0"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install numpy
    echo You may need Python 3.12 instead of 3.13
    pause
    exit /b 1
)

echo [2/10] Installing pandas...
pip install pandas

echo [3/10] Installing opencv-python...
pip install opencv-python

echo [4/10] Installing pillow...
pip install pillow

echo [5/10] Installing requests...
pip install requests

echo [6/10] Installing scipy...
pip install scipy

echo [7/10] Installing scikit-image...
pip install scikit-image

echo [8/10] Installing openpyxl...
pip install openpyxl

echo [9/10] Installing imgaug...
pip install imgaug

echo [10/10] Installing imagecorruptions...
pip install imagecorruptions

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Installed packages:
python -m pip list
echo.
echo You can now run: .\run_with_env.bat GUI.py
pause
