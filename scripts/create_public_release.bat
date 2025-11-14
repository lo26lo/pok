@echo off
REM ================================================================
REM Lanceur pour la publication publique
REM ================================================================
REM Usage: create_public_release.bat https://github.com/user/repo.git
REM ================================================================

setlocal

if "%~1"=="" (
    echo.
    echo ================================================================
    echo   Script de Publication Publique
    echo ================================================================
    echo.
    echo Usage: %~nx0 ^<URL_DU_REPOSITORY^> [VERSION]
    echo.
    echo Exemples:
    echo   %~nx0 https://github.com/lo26lo/Pokemon-Dataset-Creator.git
    echo   %~nx0 https://github.com/user/repo.git v3.3
    echo.
    echo ================================================================
    exit /b 1
)

set REPO_URL=%~1
set VERSION=%~2

if "%VERSION%"=="" (
    set VERSION=v3.2
)

echo.
echo ================================================================
echo   Lancement de la publication publique
echo ================================================================
echo.
echo Repository: %REPO_URL%
echo Version:    %VERSION%
echo.
echo Appuyez sur une touche pour continuer ou Ctrl+C pour annuler...
pause >nul

powershell -ExecutionPolicy Bypass -File "%~dp0create_public_release.ps1" -RepoUrl "%REPO_URL%" -Version "%VERSION%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================
    echo   PUBLICATION REUSSIE !
    echo ================================================================
    echo.
) else (
    echo.
    echo ================================================================
    echo   ERREUR LORS DE LA PUBLICATION
    echo ================================================================
    echo.
)

endlocal
pause
