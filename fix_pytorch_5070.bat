@echo off
echo ==========================================
echo Fix PyTorch for RTX 5070 (sm_120)
echo ==========================================
echo.
echo [INFO] Your RTX 5070 Laptop GPU requires PyTorch Nightly
echo [INFO] Stable PyTorch only supports up to sm_90
echo [INFO] RTX 5070 has compute capability sm_120
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
echo [INFO] Checking current PyTorch version...
python -c "import torch; print('Current PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"

echo.
echo ==========================================
echo OPTIONS FOR RTX 5070 (sm_120) SUPPORT:
echo ==========================================
echo.
echo Option 1: Install PyTorch Nightly (may be unstable)
echo   pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124
echo.
echo Option 2: Use CPU-only PyTorch for now (stable, but slower)
echo   Current installation will work but training will use CPU
echo.
echo Option 3: Wait for PyTorch 2.7+ stable release with sm_120 support
echo   Monitor: https://pytorch.org/get-started/locally/
echo.
echo ==========================================
echo.

:MENU
echo What would you like to do?
echo [1] Install PyTorch Nightly (GPU support for RTX 5070)
echo [2] Keep current installation (CPU-only training)
echo [3] Exit
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto INSTALL_NIGHTLY
if "%choice%"=="2" goto CPU_ONLY
if "%choice%"=="3" goto END
echo Invalid choice!
goto MENU

:INSTALL_NIGHTLY
echo.
echo [WARN] PyTorch Nightly builds may be unstable!
echo [WARN] This is experimental and may break compatibility.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto MENU

echo.
echo [INFO] Uninstalling current PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo [INFO] Installing PyTorch Nightly with CUDA 12.4...
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124

echo.
echo [INFO] Verifying installation...
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo [INFO] Testing GPU compute capability...
python tests/test_cuda.py

echo.
echo [SUCCESS] PyTorch Nightly installed!
echo [INFO] If you still see warnings, PyTorch may need more time to add sm_120 support.
goto END

:CPU_ONLY
echo.
echo [INFO] Keeping current installation
echo [INFO] Training will use CPU (slower but stable)
echo [INFO] To use GPU later, run this script again or check PyTorch website for updates
goto END

:END
echo.
pause
