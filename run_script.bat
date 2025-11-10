@echo off
REM ============================================================================
REM run_script.bat - Exécute UN script spécifique dans le venv
REM ============================================================================
REM 
REM Usage: run_script.bat <nom_du_script>
REM Exemple: run_script.bat init_prices
REM
REM Ce fichier utilise le venv si le script le nécessite.
REM IMPORTANT: Ne jamais modifier ce fichier sans mettre à jour SCRIPTS_REFERENCE.py!
REM
REM ============================================================================

if "%~1"=="" (
    echo [ERREUR] Vous devez specifier un nom de script!
    echo.
    echo Usage: run_script.bat ^<nom_du_script^>
    echo.
    echo Pour voir la liste des scripts disponibles:
    echo   python scripts\SCRIPTS_REFERENCE.py --list
    echo.
    pause
    exit /b 1
)

echo ============================================================================
echo        EXECUTION DU SCRIPT: %~1
echo ============================================================================
echo.

REM Vérifier si le venv existe (nécessaire pour SCRIPTS_REFERENCE.py)
if not exist ".venv\Scripts\python.exe" (
    echo [ERREUR] Le venv n'existe pas!
    echo.
    echo Veuillez d'abord executer install_env.bat pour creer l'environnement.
    echo.
    pause
    exit /b 1
)

REM Activer le venv
echo [INFO] Activation du venv...
call .venv\Scripts\activate.bat

REM Exécuter le script via SCRIPTS_REFERENCE.py
echo.
echo [INFO] Execution du script %~1...
echo.
python scripts\SCRIPTS_REFERENCE.py --run %~1 %2 %3 %4 %5 %6 %7 %8 %9

set ERRORLEVEL_SCRIPT=%ERRORLEVEL%

echo.
echo ============================================================================
if %ERRORLEVEL_SCRIPT% EQU 0 (
    echo                       SCRIPT TERMINE! ✅
) else (
    echo                       SCRIPT ECHOUE! ❌
)
echo ============================================================================
echo.

pause
exit /b %ERRORLEVEL_SCRIPT%
