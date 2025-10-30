@echo off
REM Lancement du GUI sans fenêtre console
cd /d "%~dp0"

REM Vérifier si l'environnement virtuel existe
if not exist ".venv\Scripts\pythonw.exe" (
    echo Environnement virtuel non trouve. Lancement de run_gui_v2_with_env.bat...
    call run_gui_v2_with_env.bat
    exit /b
)

REM Lancer avec pythonw.exe (pas de console)
start "" ".venv\Scripts\pythonw.exe" "GUI_v2.py"
