@echo off
:: Test Detection avec Prix
:: ========================
:: IMPORTANT: Utilise TOUJOURS le venv pour garantir la cohérence
:: ============================================================================

echo.
echo ========================================
echo   TEST DETECTION AVEC PRIX
echo ========================================
echo.

REM Vérifier si le venv existe
if not exist ".venv\Scripts\python.exe" (
    echo [ERREUR] Le venv n'existe pas!
    echo Veuillez executer install_env.bat pour creer l'environnement.
    pause
    exit /b 1
)

REM Activer le venv
echo [INFO] Activation du venv...
call .venv\Scripts\activate.bat

echo.
echo [1/3] Test CLI - Webcam
echo.
echo Commande:
echo   python core/detection_with_prices.py --source 0 --conf 0.5
echo.
pause

echo.
echo [2/3] Test CLI - Image
echo.
echo Commande:
echo   python core/detection_with_prices.py --source images/sv08_019_en.png --output test_result.png
echo.
pause

echo.
echo [3/3] Test GUI
echo.
echo 1. Lance le GUI: python GUI_v3.1_modern.py
echo 2. Va dans l'onglet "Detection"
echo 3. Coche "Show Prices"
echo 4. Clique sur "START WEBCAM"
echo.
pause

echo.
echo ========================================
echo   TESTS TERMINES!
echo ========================================
echo.
pause
