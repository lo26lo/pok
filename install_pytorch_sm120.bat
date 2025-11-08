@echo off
echo ==========================================
echo Install PyTorch for sm_120 (RTX 5070)
echo ==========================================
echo.

REM Check if .venv exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo [INFO] Current PyTorch version:
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"

echo.
echo ==========================================
echo Trying different PyTorch builds for sm_120 support
echo ==========================================
echo.

echo [OPTION 1] PyTorch 2.7.0 dev (pre-release)
echo [OPTION 2] PyTorch Nightly cu126
echo [OPTION 3] PyTorch custom build from conda-forge
echo [OPTION 4] Keep current and force CPU
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto TRY_27_DEV
if "%choice%"=="2" goto TRY_NIGHTLY_126
if "%choice%"=="3" goto TRY_CONDA
if "%choice%"=="4" goto KEEP_CURRENT
echo Invalid choice!
goto END

:TRY_27_DEV
echo.
echo [INFO] Trying PyTorch 2.7.0 development build...
echo [INFO] Uninstalling current PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo [INFO] Installing PyTorch 2.7.0 dev with CUDA 12.6...
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu126

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation failed!
    goto END
)

echo.
echo [INFO] Testing GPU detection...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'); print('Compute Cap:', torch.cuda.get_device_capability(0) if torch.cuda.is_available() else 'N/A')"
goto END

:TRY_NIGHTLY_126
echo.
echo [INFO] Trying PyTorch Nightly cu126...
echo [INFO] Uninstalling current PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo [INFO] Installing PyTorch Nightly cu126...
pip install --pre torch torchvision --index-url https://download.pytorch.org/whl/nightly/cu126

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Installation failed!
    goto END
)

echo.
echo [INFO] Testing GPU detection...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'); print('Compute Cap:', torch.cuda.get_device_capability(0) if torch.cuda.is_available() else 'N/A')"
goto END

:TRY_CONDA
echo.
echo [INFO] Conda-forge builds require conda/mamba installation
echo [INFO] This option is not yet implemented
echo [INFO] You can try manually:
echo   conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch-nightly -c nvidia
goto END

:KEEP_CURRENT
echo.
echo [INFO] Keeping current PyTorch installation
echo [INFO] Training will fail with sm_120 GPU
echo [INFO] Consider using CPU or waiting for official sm_120 support
goto END

:END
echo.
echo ==========================================
pause
