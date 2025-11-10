@echo off
REM ============================================================================
REM run_test.bat - Exécute UN test spécifique dans le venv
REM ============================================================================
REM 
REM Usage: run_test.bat <nom_du_test>
REM Exemple: run_test.bat test_cuda
REM
REM Ce fichier utilise TOUJOURS le venv pour garantir un environnement cohérent.
REM IMPORTANT: Ne jamais modifier ce fichier sans utiliser le venv!
REM
REM ============================================================================

if "%~1"=="" (
    echo [ERREUR] Vous devez specifier un nom de test!
    echo.
    echo Usage: run_test.bat ^<nom_du_test^>
    echo.
    echo Pour voir la liste des tests disponibles:
    echo   python scripts\SCRIPTS_REFERENCE.py --list-tests
    echo.
    pause
    exit /b 1
)

echo ============================================================================
echo        EXECUTION DU TEST: %~1
echo        Environnement Virtuel (.venv)
echo ============================================================================
echo.

REM Vérifier si le venv existe
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

REM Exécuter le test via SCRIPTS_REFERENCE.py
echo.
echo [INFO] Execution du test %~1...
echo.
python scripts\SCRIPTS_REFERENCE.py --test %~1 %2 %3 %4 %5 %6 %7 %8 %9

set ERRORLEVEL_TEST=%ERRORLEVEL%

echo.
echo ============================================================================
if %ERRORLEVEL_TEST% EQU 0 (
    echo                         TEST REUSSI! ✅
) else (
    echo                         TEST ECHOUE! ❌
)
echo ============================================================================
echo.

pause
exit /b %ERRORLEVEL_TEST%
