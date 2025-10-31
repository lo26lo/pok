@echo off
cd /d "%~dp0"

REM Activer environnement virtuel et lancer GUI v3 sans fenêtre CMD
start /B "" .venv\Scripts\pythonw.exe GUI_v3_modern.py
