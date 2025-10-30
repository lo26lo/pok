@echo off
echo ========================================
echo Test de mosaic.py
echo ========================================
echo.
echo Parametres: layout_mode=1, background_mode=0, transform_mode=0
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo Lancement de mosaic.py...
python mosaic.py 1 0 0

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo Succes: Script de mosaique termine avec succes.
    echo Verification des resultats...
    if exist output\yolov8\images (
        powershell -Command "(Get-ChildItem output\yolov8\images\*.jpg, output\yolov8\images\*.png | Measure-Object).Count"
        echo mosaiques generees dans output\yolov8\images\
    )
) else (
    echo Erreur: Le script a echoue avec le code %ERRORLEVEL%
)
echo ========================================
pause
