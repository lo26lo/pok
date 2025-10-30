@echo off
REM Script pour créer l'executable Windows du Pokemon Dataset Generator
echo ========================================
echo   Creation de l'Executable Windows
echo   Pokemon Dataset Generator v2.0
echo ========================================
echo.

REM Se placer à la racine du projet (dossier parent)
cd /d "%~dp0\.."

REM Vérifier l'environnement virtuel
if not exist ".venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo.
    echo Veuillez d'abord executer: install_env.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Activation de l'environnement virtuel...
call .venv\Scripts\activate

echo [OK] Lancement du script de creation d'executable...
echo.
echo ======================================================
echo   IMPORTANT: Cela peut prendre 5-10 minutes
echo   PyInstaller va telecharger et empaqueter toutes
echo   les dependances necessaires
echo ======================================================
echo.
pause

python tools\create_exe.py

echo.
echo ========================================
echo   Creation terminee !
echo ========================================
pause
