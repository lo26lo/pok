@echo off
REM ============================================================
REM Pokemon Dataset Generator v3.0 - Purge des fichiers obsolètes
REM ============================================================
REM Description: Supprime les fichiers GUI v2 et backups temporaires
REM Date: 2024
REM ============================================================

title Purge des fichiers obsolètes

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Purge des fichiers obsolètes - GUI v3.0            ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Ce script va supprimer les fichiers suivants :
echo.
echo [GUI v2 Obsolète]
echo   - GUI_v2.py
echo   - run_gui_v2_with_env.bat
echo   - docs\README_GUI_V2.md
echo   - docs\CHANGELOG_GUI_V2.md
echo.
echo [Fichiers temporaires]
echo   - README_V3.md (copié dans README.md)
echo   - README_OLD_BACKUP.md (backup temporaire)
echo.
echo ───────────────────────────────────────────────────────
echo.

set /p confirm="Voulez-vous continuer ? [O/N] "
if /i not "%confirm%"=="O" (
    echo.
    echo Opération annulée.
    pause
    exit /b 0
)

echo.
echo ───────────────────────────────────────────────────────
echo Suppression en cours...
echo ───────────────────────────────────────────────────────
echo.

REM Suppression de GUI v2
if exist "GUI_v2.py" (
    del "GUI_v2.py"
    echo [OK] GUI_v2.py supprimé
) else (
    echo [INFO] GUI_v2.py déjà supprimé
)

if exist "run_gui_v2_with_env.bat" (
    del "run_gui_v2_with_env.bat"
    echo [OK] run_gui_v2_with_env.bat supprimé
) else (
    echo [INFO] run_gui_v2_with_env.bat déjà supprimé
)

if exist "docs\README_GUI_V2.md" (
    del "docs\README_GUI_V2.md"
    echo [OK] docs\README_GUI_V2.md supprimé
) else (
    echo [INFO] docs\README_GUI_V2.md déjà supprimé
)

if exist "docs\CHANGELOG_GUI_V2.md" (
    del "docs\CHANGELOG_GUI_V2.md"
    echo [OK] docs\CHANGELOG_GUI_V2.md supprimé
) else (
    echo [INFO] docs\CHANGELOG_GUI_V2.md déjà supprimé
)

REM Suppression des fichiers temporaires
if exist "README_V3.md" (
    del "README_V3.md"
    echo [OK] README_V3.md supprimé (copié dans README.md)
) else (
    echo [INFO] README_V3.md déjà supprimé
)

if exist "README_OLD_BACKUP.md" (
    del "README_OLD_BACKUP.md"
    echo [OK] README_OLD_BACKUP.md supprimé
) else (
    echo [INFO] README_OLD_BACKUP.md déjà supprimé
)

echo.
echo ───────────────────────────────────────────────────────
echo Purge terminée !
echo ───────────────────────────────────────────────────────
echo.
echo [SUCCÈS] Tous les fichiers obsolètes ont été supprimés.
echo.
echo Fichiers conservés :
echo   ✅ GUI_v3_modern.py (interface moderne v3.0)
echo   ✅ run_gui_v3.bat (lanceur GUI v3.0)
echo   ✅ README.md (documentation v3.0)
echo   ✅ HELP.md (guide utilisateur)
echo   ✅ docs\GUI_V3_GUIDE.md (guide complet v3.0)
echo.
echo Vous pouvez maintenant utiliser GUI v3.0 en toute sécurité !
echo.

pause
