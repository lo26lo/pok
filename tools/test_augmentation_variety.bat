@echo off
REM Script de test pour visualiser la variété des augmentations
echo ========================================
echo Test de Variete des Augmentations
echo ========================================
echo.

if not exist .venv (
    echo ERREUR: Environnement virtuel non trouve!
    echo Lancez install_env.bat d'abord.
    pause
    exit /b 1
)

echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

echo.
echo Lancement du test (genere 10 augmentations d'une carte)...
python test_augmentation_variety.py

echo.
echo ========================================
echo Test termine ! 
echo Verifiez le dossier: test_augmentation_output/
echo ========================================
pause
