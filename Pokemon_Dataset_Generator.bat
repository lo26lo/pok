@echo off
REM Lancement du GUI sans fenêtre console
cd /d "%~dp0"
wscript.exe "%~dp0invisible.vbs" "%~dp0run_gui_silent.bat"
