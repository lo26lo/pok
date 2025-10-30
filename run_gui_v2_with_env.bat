@echo off 
echo ========================================
echo   Pokemon Dataset Generator v2.0
echo   (Using Python 3.12 Virtual Environment)
echo ========================================
echo.

cd /d "%~dp0"

REM Verifier si l'environnement virtuel existe
if not exist ".venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo.
    echo Veuillez d'abord executer: install_env.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Activation de l'environnement virtuel Python 3.12...
call .venv\Scripts\activate

echo [OK] Lancement du GUI v2.0...
echo.

python GUI_v2.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Le GUI a rencontre une erreur
    echo.
)

pause
