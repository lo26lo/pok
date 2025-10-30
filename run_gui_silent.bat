@echo off
REM Lancement silencieux du GUI (sans console)
cd /d "%~dp0"

REM Vérifier l'environnement virtuel
if not exist ".venv\Scripts\python.exe" (
    start "" run_gui_v2_with_env.bat
    exit
)

REM Lancer le GUI sans console avec pythonw.exe
start "" ".venv\Scripts\pythonw.exe" "GUI_v2.py"
