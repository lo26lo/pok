@echo off
echo ==========================================
echo Test PyTorch GPU Detection
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo [INFO] Testing PyTorch installation...
python tests/test_cuda.py

echo.
echo ==========================================
pause
