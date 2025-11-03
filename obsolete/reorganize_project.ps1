# Script de réorganisation du projet Pokemon Dataset Generator V3.1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Reorganization Pokemon Dataset V3.1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Créer les dossiers
Write-Host "[1/4] Creating folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "obsolete" | Out-Null
New-Item -ItemType Directory -Force -Path "excel" | Out-Null
Write-Host "  ✓ Folders created" -ForegroundColor Green

# 2. Déplacer fichiers obsolètes
Write-Host ""
Write-Host "[2/4] Moving obsolete files..." -ForegroundColor Yellow

$obsoleteFiles = @(
    "GUI_v3_modern.py",
    "harmonize_views.py",
    "api_server.py",
    "test_tcgdex_surging.py",
    "ANALYSE_COHERENCE.md",
    "CHANGELOG_V4.md",
    "COMMIT_IMAGE_DOWNLOAD.md",
    "CORRECTIONS_RAPPORT_FINAL.md",
    "CORRECTIONS_RESUME.md",
    "FINALISATION_DOCUMENTATION.md",
    "NOUVELLES_FONCTIONNALITES.md",
    "SESSION_COMPLETE_2025-10-31.md",
    "VERIFICATION_GUIDE.md",
    "validation_report.html",
    "purge_obsolete_files.bat",
    "run_gui_v3.bat",
    "fix_font_button.ps1",
    "fix_settings_font.py"
)

$movedCount = 0
foreach ($file in $obsoleteFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "obsolete\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Green
        $movedCount++
    }
}
Write-Host "  → $movedCount files moved to obsolete/" -ForegroundColor Cyan

# 3. Déplacer fichiers Excel
Write-Host ""
Write-Host "[3/4] Moving Excel files..." -ForegroundColor Yellow

$excelFiles = @(
    "cards_info.xlsx",
    "cards_info_updated.xlsx",
    "cards_list.xlsx",
    "cards_with_prices.xlsx",
    "extension_cards.xlsx"
)

$excelMoved = 0
foreach ($file in $excelFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "excel\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Green
        $excelMoved++
    }
}
Write-Host "  → $excelMoved Excel files moved to excel/" -ForegroundColor Cyan

# 4. Mettre à jour les chemins dans les fichiers
Write-Host ""
Write-Host "[4/4] Updating paths in files..." -ForegroundColor Yellow

$filesToUpdate = @(
    "GUI_v3.1_modern.py",
    "tools\check_excel.py",
    "tools\create_exe.py",
    "pokemon_dataset_generator.spec",
    "gui_config.json"
)

$updateCount = 0
foreach ($file in $filesToUpdate) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        $originalContent = $content
        
        # Remplacer les chemins Excel (double quotes)
        $content = $content -replace '"cards_info\.xlsx"', '"excel/cards_info.xlsx"'
        $content = $content -replace '"cards_info_updated\.xlsx"', '"excel/cards_info_updated.xlsx"'
        $content = $content -replace '"cards_list\.xlsx"', '"excel/cards_list.xlsx"'
        $content = $content -replace '"cards_with_prices\.xlsx"', '"excel/cards_with_prices.xlsx"'
        $content = $content -replace '"extension_cards\.xlsx"', '"excel/extension_cards.xlsx"'
        
        # Remplacer les chemins Excel (simple quotes)
        $content = $content -replace "'cards_info\.xlsx'", "'excel/cards_info.xlsx'"
        $content = $content -replace "'cards_info_updated\.xlsx'", "'excel/cards_info_updated.xlsx'"
        $content = $content -replace "'cards_list\.xlsx'", "'excel/cards_list.xlsx'"
        $content = $content -replace "'cards_with_prices\.xlsx'", "'excel/cards_with_prices.xlsx'"
        $content = $content -replace "'extension_cards\.xlsx'", "'excel/extension_cards.xlsx'"
        
        # Cas spécial pour Path() dans GUI
        $content = $content -replace 'Path\("cards_info\.xlsx"\)', 'Path("excel/cards_info.xlsx")'
        $content = $content -replace 'Path\("cards_list\.xlsx"\)', 'Path("excel/cards_list.xlsx")'
        
        # Cas spécial pour --add-data dans create_exe.py
        $content = $content -replace '--add-data=cards_info\.xlsx;\.', '--add-data=excel/cards_info.xlsx;excel'
        
        # Cas spécial pour datas dans .spec
        $content = $content -replace "\('cards_info\.xlsx', '\.'", "('excel/cards_info.xlsx', 'excel'"
        
        if ($content -ne $originalContent) {
            $content | Set-Content $file -Encoding UTF8 -NoNewline
            Write-Host "  ✓ Updated: $file" -ForegroundColor Green
            $updateCount++
        }
    }
}
Write-Host "  → $updateCount files updated" -ForegroundColor Cyan

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Reorganization completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  • Obsolete files moved: $movedCount" -ForegroundColor White
Write-Host "  • Excel files moved: $excelMoved" -ForegroundColor White
Write-Host "  • Files updated: $updateCount" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test the application: .\run_gui_v3.1.bat" -ForegroundColor White
Write-Host "  2. Update .gitignore: add 'excel/*.xlsx'" -ForegroundColor White
Write-Host "  3. Commit: git add . && git commit -m 'Reorganize: obsolete + excel folders'" -ForegroundColor White
