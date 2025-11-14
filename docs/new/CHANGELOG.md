# 📜 Changelog - Pokémon Dataset Generator

**Version actuelle** : 3.3.1  
**Dernière mise à jour** : 14 novembre 2025

---

## [3.3.1] - 2025-11-14

### 📚 Documentation Audit & Cleanup

**Image References Fixed**
- ❌ Supprimé 5 références à images manquantes
- ✅ Remplacé par texte descriptif
- ✅ Gallery README.md : 2×2 → 1×2 (images existantes uniquement)

**Excel → YAML Migration**
- ✅ Toutes références Excel migrées vers YAML
- `excel/cards_with_prices.xlsx` → `models/cards_database.yaml`
- Mis à jour dans 10+ fichiers documentation

**Version Standardization**
- ✅ Unification de toute la documentation : **v3.2**
- HELP.md, FEATURES.md, GUI_V3_GUIDE.md, README_COMPLET.md
- Dates mises à jour : 14 novembre 2025

**Documentation Verification**
- ✅ Audit complet de 34+ fichiers markdown
- ✅ 8 Settings tabs documentés partout
- ✅ 11 vues fonctionnelles référencées correctement

---

## [3.3.0] - 2025-11-14

### 📚 Documentation Refactoring

**BREAKING CHANGE** : Refonte complète de la structure documentation

**Nouveau README.md**
- ✅ Design "landing page" visuel
- ✅ Overview haut niveau + liens détaillés

**Documentation Modulaire**
- ✅ Création `docs/features/` (4 fichiers)
  - `1_GUI_OVERVIEW.md`
  - `2_DATASET_GENERATION.md`
  - `3_TRAINING_AND_DETECTION.md`
  - `4_PRICE_SYSTEM.md`

**Améliorations**
- ✅ Navigation entre documents
- ✅ Liens images GitHub absolus
- ✅ Settings : 6 → 8 tabs (Advanced + Debug)

---

## [3.2.4] - 2025-11-12

### ⚙️ Settings Enhancement - Debug Tab

**NEW : 8ème Tab "Debug"**

**Device Configuration** :
- ✅ Auto (GPU si dispo, sinon CPU)
- ✅ CPU Only (forcer CPU)
- ✅ GPU 0/GPU 1 (multi-GPU)

**Performance Settings** :
- ✅ Worker count (1-32, auto-détection cores CPU)
- ✅ Cache mode : RAM / Disk / Disabled

**Logging Configuration** :
- ✅ Log level : ERROR, WARNING, INFO, DEBUG, TRACE
- ✅ Save debug logs : `debug_logs/<timestamp>.log`

**Advanced Debug** :
- ✅ Performance profiling (temps d'exécution fonctions)
- ✅ Benchmark logging (métriques détaillées)
- ✅ Multiprocessing debug
- ✅ Memory profiling (suivi RAM)

**Persistence** : `gui_config.json`

---

## [3.2.3] - 2025-11-12

### 🔧 Configuration System

**Path Centralization**
- ✅ Tous les chemins dans `config/paths.json`
- ✅ Facilite déplacement du projet
- ✅ Chemins configurables via Settings

**Structure paths.json** :
```json
{
  "images": "images/",
  "output": "output/",
  "models": "models/",
  "excel": "excel/",
  "runs": "runs/"
}
```

---

## [3.2.2] - 2025-11-11

### ⚡ Holographic Performance Optimization

**100-300× SPEEDUP !** 🚀

**Optimisations v3.2.2** :
- ✅ GPU acceleration (CUDA kernels custom)
- ✅ LUT (Look-Up Tables) pré-calculées
- ✅ Separable filters (convolution 2D → 2× 1D)
- ✅ Half-precision (FP16) pour calculs GPU
- ✅ Multi-threading (4 threads/style)

**Performance** :

| Style | Avant | Après | Speedup |
|-------|-------|-------|---------|
| Rainbow | 2.5s | 0.025s | **100×** |
| Metallic | 3.0s | 0.01s | **300×** |
| Glitter | 1.8s | 0.015s | **120×** |
| Prismatic | 4.2s | 0.018s | **233×** |
| Sparkle | 2.0s | 0.012s | **167×** |

**Impact** : Holographic sur 1000 images : 3000s → 15s (5 min → 15 sec)

**Fichiers** :
- `core/holographic_augmenter_optimized.py` (nouvelle version)
- `core/holographic_augmenter.py` (ancienne, conservée)

---

## [3.2.1] - 2025-11-10

### ⚡ Mosaic Performance Optimization

**30-60× SPEEDUP !** 🚀

**Optimisations v3.2.1** :
- ✅ Vectorisation NumPy (pas de boucles Python)
- ✅ Pré-allocation mémoire (pas de `np.append`)
- ✅ OpenCV optimisé (hardware-accelerated)
- ✅ Batch processing (10 images à la fois)
- ✅ Cache backgrounds (pas de reload répété)

**Performance** :

| Configuration | Avant | Après | Speedup |
|---------------|-------|-------|---------|
| 100 mosaics Quick | 180s | 6s | **30×** |
| 100 mosaics Standard | 420s | 12s | **35×** |
| 500 mosaics Complete | 2400s | 40s | **60×** |

**Mémoire** : ~500 MB pour 1000 mosaïques (batch processing)

**Fichiers** :
- `core/mosaic_optimized.py` (nouvelle version)
- `core/mosaic.py` (ancienne, conservée)

**Documentation** :
- `docs/PERFORMANCE_OPTIMIZATION_SUMMARY.md`
- `docs/PERFORMANCE_BEST_PRACTICES.md`

---

## [3.2.0] - 2025-11-09

### 🎨 GUI v3.2 - Modern Design

**Design System v3.2** :
- ✅ Palette Catppuccin Mocha
- ✅ Architecture 3 zones (Header, Sidebar, Main)
- ✅ Sidebar collapsible
- ✅ Dark theme moderne

**11 Vues Fonctionnelles** :
1. Home (Dashboard)
2. Workflow (Automatique)
3. Image Download
4. Augmentation
5. Fake Images
6. Mosaic Generator
7. Validation
8. Training
9. Detection
10. Export
11. Tools

**Dashboard Amélioré** :
- ✅ 4 stats cards temps réel
- ✅ Quick actions (4 boutons)
- ✅ Environment status (Python, GPU, VRAM)
- ✅ Auto-refresh (5 sec)

**Settings Dialog 8 Tabs** :
1. General
2. Augmentation
3. Mosaic
4. Training
5. Detection
6. Export
7. Advanced
8. Debug (nouveau v3.2.4)

---

## [3.1.0] - 2025-11-05

### 🔌 TCGdex API Integration

**TCGdex v2 API** :
- ✅ 10 langues supportées
- ✅ 13+ sets populaires
- ✅ Parallel downloads (5 threads)
- ✅ Prix Cardmarket + TCGPlayer

**Image Downloader** :
- ✅ GUI intégré (vue Image Download)
- ✅ Sélection set + langue
- ✅ Progression temps réel
- ✅ Retry automatique (3 tentatives)

**Price System** :
- ✅ Base de données YAML (`models/cards_database.yaml`)
- ✅ Overlay prix sur détections
- ✅ Mise à jour manuelle/automatique
- ✅ Excel import/export

**Fichiers** :
- `core/tcgdex_api.py`
- `core/image_downloader.py`
- `core/detection_with_prices.py`

---

## [3.0.0] - 2025-11-01

### 🚀 Major Release - Complete Rewrite

**Architecture** :
- ✅ Séparation GUI / Core
- ✅ 16 modules core/
- ✅ Managers (workflow, training, detection)

**Core Modules** :
- `augmentation.py` (22 techniques imgaug)
- `mosaic.py` (3 modes, 3 layouts)
- `holographic_augmenter.py` (5 styles)
- `auto_balancer.py` (3 stratégies)
- `dataset_validator.py` (5 checks)
- `dataset_exporter.py` (4 formats)
- `workflow_manager.py` (pipeline automatique)
- `training_manager.py` (YOLOv8/v11)
- `detection_manager.py` (3 modes)

**YOLO Support** :
- ✅ YOLOv8 (n/s/m/l/x)
- ✅ YOLO11 (n/s)
- ✅ Entraînement GUI
- ✅ Détection temps réel

**Export Formats** :
- ✅ COCO JSON
- ✅ Pascal VOC XML
- ✅ TFRecord (TensorFlow)
- ✅ Roboflow

---

## [2.5.0] - 2025-10-20

### 📊 Excel & Prices

**Excel Integration** :
- ✅ Template génération
- ✅ Import/Export prix
- ✅ Class ID mapping

**Price Database** :
- ✅ Cardmarket EUR
- ✅ TCGPlayer USD
- ✅ Auto-update API

---

## [2.0.0] - 2025-10-10

### 🎨 GUI v2.0

**Première GUI** :
- ✅ Tkinter moderne
- ✅ 6 tabs fonctionnels
- ✅ Logs temps réel
- ✅ Progression bars

**Fonctionnalités** :
- ✅ Augmentation (15 techniques)
- ✅ Mosaïques basiques
- ✅ Validation dataset
- ✅ Auto-balancer

---

## [1.0.0] - 2025-09-15

### 🎉 Initial Release

**Scripts CLI** :
- ✅ Augmentation basique
- ✅ Génération labels YOLO
- ✅ Validation images

**YOLO** :
- ✅ YOLOv8 support
- ✅ Format annotations

---

**Légende** :
- ✅ Ajouté
- 🔄 Modifié
- ❌ Supprimé
- 🐛 Bug fix
- ⚡ Performance
- 📚 Documentation
- 🔧 Configuration

**Format** : [Version] - Date - Type de changement
