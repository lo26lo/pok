@echo off
REM Script pour installer PyTorch avec CUDA 12.4 pour RTX 40xx/50xx
REM Usage: fix_pytorch_cuda.bat

echo ==========================================
echo Fix PyTorch CUDA for RTX 40xx/50xx
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

echo.
echo [INFO] Checking current PyTorch version...
python -c "import torch; print('Current PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if hasattr(torch.version, 'cuda') else 'N/A')"

echo.
echo [INFO] This will reinstall PyTorch with CUDA 12.4 support
echo [INFO] Required for RTX 40xx/50xx series GPUs
echo.
pause

echo.
echo [INFO] Uninstalling current PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo [INFO] Installing PyTorch with CUDA 12.4...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo.
echo [INFO] Verifying installation...
python -c "import torch; print('New PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if hasattr(torch.version, 'cuda') else 'N/A'); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo ==========================================
echo Installation completed!
echo ==========================================
echo.
echo You can now train YOLO models with GPU acceleration.
echo.
pause
