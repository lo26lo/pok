@echo off
REM ============================================================================
REM run_all_tests.bat - Exécute TOUS les tests dans le venv
REM ============================================================================
REM 
REM Ce fichier utilise TOUJOURS le venv pour garantir un environnement cohérent.
REM IMPORTANT: Ne jamais modifier ce fichier sans utiliser le venv!
REM
REM ============================================================================

echo ============================================================================
echo        EXECUTION DE TOUS LES TESTS - Environnement Virtuel (.venv)
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

REM Exécuter tous les tests via SCRIPTS_REFERENCE.py
echo.
echo [INFO] Execution de tous les tests...
echo.
python scripts\SCRIPTS_REFERENCE.py --run-all-tests

REM Capturer le code de retour
set ERRORLEVEL_TEST=%ERRORLEVEL%

echo.
echo ============================================================================
if %ERRORLEVEL_TEST% EQU 0 (
    echo                    TOUS LES TESTS SONT PASSES! ✅
) else (
    echo                    CERTAINS TESTS ONT ECHOUE! ❌
)
echo ============================================================================
echo.

pause
exit /b %ERRORLEVEL_TEST%
