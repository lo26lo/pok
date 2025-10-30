@echo off
REM fix_numpy_conflict.bat - Fix NumPy 2.x conflict caused by opencv-python
cd /d "%~dp0"

if not exist ".venv\Scripts\activate" (
    echo ERROR: .venv not found. Run install_env.bat first.
    pause
    exit /b 1
)

echo ========================================
echo Fixing NumPy 2.x conflict
echo ========================================
echo.
echo This will:
echo 1. Uninstall NumPy 2.x and opencv-python
echo 2. Install NumPy 1.26.4
echo 3. Install opencv-python 4.9.x (compatible with NumPy 1.x)
echo 4. Install remaining dependencies
echo.

call .venv\Scripts\activate

echo Step 1: Removing conflicting packages...
pip uninstall -y numpy opencv-python

echo.
echo Step 2: Installing NumPy 1.26.4...
pip install "numpy==1.26.4"

echo.
echo Step 3: Installing opencv-python 4.9.x (NumPy 1.x compatible)...
pip install "opencv-python<4.10.0"

echo.
echo Step 4: Installing remaining packages...
pip install pandas pillow requests scipy scikit-image openpyxl imgaug imagecorruptions

echo.
echo ========================================
echo Verification
echo ========================================
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
python -c "import imgaug; print('imgaug: OK')"

echo.
echo ========================================
echo Fix complete!
echo ========================================
echo.
echo All packages installed:
python -m pip list
echo.
pause
