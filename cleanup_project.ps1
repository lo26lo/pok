# ============================================
# Script de nettoyage du projet Pokemon Dataset Generator
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Pokemon Dataset Generator - Cleanup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Déplacer les fichiers Excel dans excel/
Write-Host "[1/4] Déplacement des fichiers Excel..." -ForegroundColor Yellow

$excelFiles = @(
    "cards_info.xlsx",
    "cards_info_updated.xlsx", 
    "cards_list.xlsx",
    "cards_with_prices.xlsx",
    "extension_cards.xlsx"
)

foreach ($file in $excelFiles) {
    if (Test-Path $file) {
        Write-Host "  -> Déplacement de $file vers excel/" -ForegroundColor Gray
        Move-Item $file excel/ -Force
    }
}

# 2. Déplacer les fichiers obsolètes
Write-Host "[2/4] Déplacement des fichiers obsolètes..." -ForegroundColor Yellow

$obsoleteFiles = @(
    "GUI_v3_modern.py",              # Remplacé par v3.1
    "harmonize_views.py",            # Script temporaire
    "api_server.py",                 # Non utilisé
    "test_tcgdex_surging.py",        # Test temporaire
    "ANALYSE_COHERENCE.md",          # Doc temporaire
    "CHANGELOG_V4.md",               # V4 abandonnée
    "COMMIT_IMAGE_DOWNLOAD.md",      # Doc temporaire
    "CORRECTIONS_RAPPORT_FINAL.md",  # Doc temporaire
    "CORRECTIONS_RESUME.md",         # Doc temporaire
    "FINALISATION_DOCUMENTATION.md", # Doc temporaire
    "NOUVELLES_FONCTIONNALITES.md",  # Doc temporaire
    "SESSION_COMPLETE_2025-10-31.md",# Doc session
    "VERIFICATION_GUIDE.md",         # Doc temporaire
    "validation_report.html",        # Rapport temporaire
    "purge_obsolete_files.bat",      # Ancien script
    "reorganize_project.ps1",        # Ancien script
    "run_gui_v3.bat",                # Remplacé par v3.1
    "fix_font_button.ps1",           # Script temporaire (si existe)
    "fix_settings_font.py"           # Script temporaire (si existe)
)

foreach ($file in $obsoleteFiles) {
    if (Test-Path $file) {
        Write-Host "  -> Déplacement de $file vers obsolete/" -ForegroundColor Gray
        Move-Item $file obsolete/ -Force
    }
}

# 3. Mettre à jour les références aux fichiers Excel dans les scripts
Write-Host "[3/4] Mise à jour des chemins Excel dans les scripts..." -ForegroundColor Yellow

$scriptsToUpdate = @(
    "GUI_v3.1_modern.py"
)

foreach ($script in $scriptsToUpdate) {
    if (Test-Path $script) {
        Write-Host "  -> Mise à jour de $script" -ForegroundColor Gray
        
        $content = Get-Content $script -Raw -Encoding UTF8
        
        # Remplacer les références aux fichiers Excel
        $content = $content -replace '"cards_info\.xlsx"', '"excel/cards_info.xlsx"'
        $content = $content -replace '"cards_info_updated\.xlsx"', '"excel/cards_info_updated.xlsx"'
        $content = $content -replace '"cards_list\.xlsx"', '"excel/cards_list.xlsx"'
        $content = $content -replace '"cards_with_prices\.xlsx"', '"excel/cards_with_prices.xlsx"'
        $content = $content -replace '"extension_cards\.xlsx"', '"excel/extension_cards.xlsx"'
        
        $content = $content -replace "'cards_info\.xlsx'", "'excel/cards_info.xlsx'"
        $content = $content -replace "'cards_info_updated\.xlsx'", "'excel/cards_info_updated.xlsx'"
        $content = $content -replace "'cards_list\.xlsx'", "'excel/cards_list.xlsx'"
        $content = $content -replace "'cards_with_prices\.xlsx'", "'excel/cards_with_prices.xlsx'"
        $content = $content -replace "'extension_cards\.xlsx'", "'excel/extension_cards.xlsx'"
        
        Set-Content $script $content -Encoding UTF8 -NoNewline
    }
}

# 4. Nettoyer les fichiers temporaires
Write-Host "[4/4] Nettoyage des fichiers temporaires..." -ForegroundColor Yellow

# Supprimer les __pycache__
if (Test-Path "__pycache__") {
    Write-Host "  -> Suppression de __pycache__/" -ForegroundColor Gray
    Remove-Item "__pycache__" -Recurse -Force
}

if (Test-Path "core/__pycache__") {
    Write-Host "  -> Suppression de core/__pycache__/" -ForegroundColor Gray
    Remove-Item "core/__pycache__" -Recurse -Force
}

# Supprimer les .pyc
$pycFiles = Get-ChildItem -Path . -Filter "*.pyc" -Recurse -Force
foreach ($pyc in $pycFiles) {
    Write-Host "  -> Suppression de $($pyc.FullName)" -ForegroundColor Gray
    Remove-Item $pyc.FullName -Force
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Nettoyage terminé !" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Résumé:" -ForegroundColor Cyan
Write-Host "  - Fichiers Excel déplacés dans excel/" -ForegroundColor White
Write-Host "  - Fichiers obsolètes déplacés dans obsolete/" -ForegroundColor White
Write-Host "  - Chemins mis à jour dans les scripts" -ForegroundColor White
Write-Host "  - Fichiers temporaires supprimés" -ForegroundColor White
Write-Host ""
Write-Host "Vous pouvez maintenant:" -ForegroundColor Yellow
Write-Host "  1. Vérifier que tout fonctionne: .\run_gui_v3.1.bat" -ForegroundColor White
Write-Host "  2. Commiter les changements: git add -A && git commit -m 'Cleanup: Réorganisation fichiers Excel et obsolètes'" -ForegroundColor White
Write-Host ""
