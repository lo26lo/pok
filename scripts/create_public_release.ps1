# ================================================================
# Script de Publication Publique sans Historique
# ================================================================
# Ce script crée un repository public propre avec un seul commit
# initial, sans exposer l'historique de développement complet.
#
# Usage: .\create_public_release.ps1 -RepoUrl "https://github.com/user/repo.git"
# ================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl,
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "v3.2",
    
    [Parameter(Mandatory=$false)]
    [string]$TempDir = "C:\DATA\pok-public-temp"
)

# Couleurs pour l'affichage
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "================================================================"
Write-Info "  Script de Publication Publique - Pokemon Dataset Generator"
Write-Info "================================================================"
Write-Info ""

# Vérifier que nous sommes dans le bon dossier
$currentDir = Get-Location
if (-not (Test-Path "GUI_v3.1_modern.py")) {
    Write-Error "❌ ERREUR: Ce script doit être exécuté depuis la racine du projet pok"
    Write-Error "   Dossier actuel: $currentDir"
    exit 1
}

Write-Info "✓ Dossier du projet: $currentDir"
Write-Info "✓ Repository cible: $RepoUrl"
Write-Info "✓ Version: $Version"
Write-Info ""

# Étape 1: Créer le dossier temporaire
Write-Info "[1/7] Création du dossier temporaire..."
if (Test-Path $TempDir) {
    Write-Warning "   Le dossier temporaire existe déjà. Suppression..."
    Remove-Item -Recurse -Force $TempDir
}
New-Item -ItemType Directory -Path $TempDir | Out-Null
Write-Success "   ✓ Dossier créé: $TempDir"
Write-Info ""

# Étape 2: Copier les fichiers (en excluant les dossiers de développement)
Write-Info "[2/7] Copie des fichiers du projet..."
Write-Info "   Exclusions:"
Write-Info "   - Dossiers: .git, .venv, __pycache__, .vscode, output, images, runs, .planning"
Write-Info "   - Fichiers: *.log, *.pyc"

$excludeDirs = @(".git", ".venv", "__pycache__", ".vscode", "output", "images", "runs", ".planning")
$excludeFiles = @("*.log", "*.pyc")

$robocopyArgs = @(
    $currentDir,
    $TempDir,
    "/E",  # Copier tous les sous-dossiers
    "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"  # Mode silencieux
)

# Ajouter les exclusions de dossiers
foreach ($dir in $excludeDirs) {
    $robocopyArgs += "/XD"
    $robocopyArgs += $dir
}

# Ajouter les exclusions de fichiers
foreach ($file in $excludeFiles) {
    $robocopyArgs += "/XF"
    $robocopyArgs += $file
}

$result = robocopy @robocopyArgs
if ($LASTEXITCODE -ge 8) {
    Write-Error "   ❌ Erreur lors de la copie des fichiers"
    exit 1
}
Write-Success "   ✓ Fichiers copiés avec succès"
Write-Info ""

# Étape 3: Initialiser le nouveau repository Git
Write-Info "[3/7] Initialisation du repository Git..."
Push-Location $TempDir
git init | Out-Null
Write-Success "   ✓ Repository Git initialisé"
Write-Info ""

# Étape 4: Ajouter tous les fichiers
Write-Info "[4/7] Ajout des fichiers au staging..."
git add -A
$fileCount = (git diff --cached --numstat | Measure-Object).Count
Write-Success "   ✓ $fileCount fichiers ajoutés"
Write-Info ""

# Étape 5: Créer le commit initial
Write-Info "[5/7] Création du commit initial..."
$commitMessage = @"
Initial release - Pokemon Dataset Generator $Version

Complete YOLO pipeline for Pokemon card detection with modern GUI:
- Dataset generation with 22+ augmentation techniques
- Holographic effects (5+ styles)
- Ultra-fast mosaic generation (30-60x faster)
- One-click YOLOv8/v11 training
- Live detection with real-time price integration
- TCGdex API integration
- Auto-balancing and validation tools
- Comprehensive documentation

Features:
✅ Modern GUI with 8-tab settings
✅ GPU acceleration support
✅ Parallel processing
✅ Debug tools and profiling
✅ Complete test suite
✅ Modular documentation structure
"@

git commit -m $commitMessage | Out-Null
Write-Success "   ✓ Commit créé: Initial release $Version"
Write-Info ""

# Étape 6: Configurer le remote et pusher
Write-Info "[6/7] Configuration du remote et push..."
git branch -M main
git remote add origin $RepoUrl

Write-Info "   Push vers $RepoUrl..."
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Error "   ❌ Erreur lors du push"
    Pop-Location
    exit 1
}
Write-Success "   ✓ Code publié avec succès !"
Write-Info ""

# Étape 7: Nettoyage
Pop-Location
Write-Info "[7/7] Nettoyage du dossier temporaire..."
Remove-Item -Recurse -Force $TempDir
Write-Success "   ✓ Dossier temporaire supprimé"
Write-Info ""

# Résumé final
Write-Info "================================================================"
Write-Success "✅ PUBLICATION RÉUSSIE !"
Write-Info "================================================================"
Write-Info ""
Write-Info "📦 Repository public:"
Write-Success "   $RepoUrl"
Write-Info ""
Write-Info "📊 Statistiques:"
Write-Info "   - 1 commit unique"
Write-Info "   - $fileCount fichiers"
Write-Info "   - Version: $Version"
Write-Info ""
Write-Info "🔒 Repository privé:"
Write-Info "   - Historique complet conservé"
Write-Info "   - Tous les commits préservés"
Write-Info ""
Write-Info "💡 Prochaines étapes recommandées:"
Write-Info "   1. Vérifier le repository sur GitHub"
Write-Info "   2. Ajouter une LICENSE (ex: MIT)"
Write-Info "   3. Créer une release GitHub"
Write-Info "   4. Configurer les settings du repository"
Write-Info ""
Write-Info "================================================================"
