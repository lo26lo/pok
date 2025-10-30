@echo off
echo ========================================
echo   Test Augmentation Rapide (5 images)
echo ========================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo Veuillez d'abord executer: install_env.bat
    pause
    exit /b 1
)

echo [OK] Activation environnement virtuel...
call .venv\Scripts\activate

echo [OK] Lancement augmentation (5 images par carte)...
echo.

python augmentation.py --num_aug 5 --target augmented

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo   Augmentation terminee avec succes!
    echo ========================================
    echo.
    echo Images generees dans: output\augmented\images\
    echo Labels YOLO dans: output\augmented\labels\
) else (
    echo ========================================
    echo   Erreur lors de l'augmentation
    echo ========================================
)

echo.
pause
