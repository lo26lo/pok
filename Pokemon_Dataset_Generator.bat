@echo off
REM ============================================================================
REM Pokemon Dataset Generator - Lanceur principal
REM ============================================================================
REM Lancement du GUI sans fenêtre console
REM IMPORTANT: Utilise TOUJOURS le venv
REM ============================================================================

cd /d "%~dp0"

REM Vérifier si l'environnement virtuel existe
if not exist ".venv\Scripts\pythonw.exe" (
    echo Environnement virtuel non trouve.
    echo Veuillez executer install_env.bat pour creer l'environnement.
    pause
    exit /b 1
)

REM Lancer le GUI v3.1 avec pythonw.exe (pas de console)
start "" ".venv\Scripts\pythonw.exe" "GUI_v3.1_modern.py"
