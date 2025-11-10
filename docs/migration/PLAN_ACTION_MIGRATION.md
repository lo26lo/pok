# 🎯 PLAN D'ACTION - Réorganisation Complète des Répertoires

## 📋 RÉSUMÉ EXÉCUTIF

**Objectif**: Réorganiser tous les répertoires de sortie pour une structure claire, cohérente et maintenable.

**Durée estimée**: 2-3 heures (migration + tests)

**Fichiers à modifier**: 
- 8 scripts core Python
- 2 fichiers GUI
- 1 fichier config JSON
- 2 scripts batch (optionnel)

---

## 🗺️ VUE D'ENSEMBLE

### Structure AVANT (problématique)
```
pok/
├── images/                    # ✅ OK
├── augment/                   # ⚠️ Confusion avec augmented
├── fakeimg/                   # ⚠️ Nom peu clair
├── fakeimg_augmented/         # ⚠️ Nom peu clair
├── output/
│   ├── augmented/ (1200)      # ⚠️ OK mais isolé
│   ├── yolov8/ (1350)         # ❌ Mélange augmented + mosaics
│   └── yolov8_test/ (1200)    # ❌ DOUBLON inutile
└── runs/                      # ✅ OK
```

### Structure APRÈS (solution)
```
pok/
├── images/                    # 🔵 SOURCE
├── backgrounds/               # 🟣 BACKGROUNDS (renommé)
│   ├── original/
│   └── augmented/
├── output/                    # 🔴 PIPELINE COMPLET
│   ├── holographic/           # Étape 1
│   ├── augmented/             # Étape 2
│   ├── mosaics/               # Étape 3
│   └── dataset/               # Étape 4 (FINAL)
└── runs/                      # 🟢 TRAINING
```

---

## ⚡ EXÉCUTION RAPIDE

### Option A: Migration Automatique (Recommandé)

```bash
# 1. Lancer le script de migration
python migrate_directories.py

# 2. Vérifier la structure
ls -R output/

# 3. Fusionner le dataset
python merge_dataset.py

# 4. ENSUITE: Mettre à jour les scripts (voir Phase 2)
```

### Option B: Migration Manuelle

Voir section "Phase 1: Migration des données" ci-dessous.

---

## 📝 PHASE 1: MIGRATION DES DONNÉES (1h)

### Étape 1.1: Backup (5 min)

```powershell
# Créer un backup complet
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
New-Item -ItemType Directory -Path "backup_$timestamp"
Copy-Item -Recurse output "backup_$timestamp/output"
Copy-Item -Recurse augment "backup_$timestamp/augment" -ErrorAction SilentlyContinue
Copy-Item -Recurse fakeimg* "backup_$timestamp/" -ErrorAction SilentlyContinue
```

### Étape 1.2: Créer nouvelle structure (5 min)

```powershell
# Créer tous les nouveaux répertoires
New-Item -ItemType Directory -Force -Path "backgrounds/original"
New-Item -ItemType Directory -Force -Path "backgrounds/augmented"
New-Item -ItemType Directory -Force -Path "output/holographic/images"
New-Item -ItemType Directory -Force -Path "output/holographic/labels"
New-Item -ItemType Directory -Force -Path "output/mosaics/images"
New-Item -ItemType Directory -Force -Path "output/mosaics/labels"
New-Item -ItemType Directory -Force -Path "output/dataset/images"
New-Item -ItemType Directory -Force -Path "output/dataset/labels"
```

### Étape 1.3: Migrer les données (20 min)

```powershell
# 1. Backgrounds
Move-Item fakeimg backgrounds/original -ErrorAction SilentlyContinue
Move-Item fakeimg_augmented backgrounds/augmented -ErrorAction SilentlyContinue

# 2. Holographic (augment/ → output/holographic/)
if (Test-Path augment) {
    Copy-Item augment/*.png output/holographic/images/
    # Créer labels basiques
    Get-ChildItem output/holographic/images/*.png | ForEach-Object {
        $label = "output/holographic/labels/$($_.BaseName).txt"
        "0 0.5 0.5 1.0 1.0" | Out-File $label
    }
    Remove-Item augment -Recurse
}

# 3. Mosaics (extraire de yolov8/)
if (Test-Path output/yolov8/images) {
    Copy-Item output/yolov8/images/layout_*.png output/mosaics/images/
    Copy-Item output/yolov8/labels/layout_*.txt output/mosaics/labels/
}

# 4. Supprimer doublons
Remove-Item output/yolov8_test -Recurse -ErrorAction SilentlyContinue
```

### Étape 1.4: Vérification (5 min)

```powershell
Write-Host "`n📊 Vérification de la structure:" -ForegroundColor Cyan
Write-Host "Images originales: $((Get-ChildItem images/*.png).Count)"
Write-Host "Backgrounds orig: $((Get-ChildItem backgrounds/original/*.png -ErrorAction SilentlyContinue).Count)"
Write-Host "Backgrounds aug: $((Get-ChildItem backgrounds/augmented/*.png -ErrorAction SilentlyContinue).Count)"
Write-Host "Holographic: $((Get-ChildItem output/holographic/images/*.png -ErrorAction SilentlyContinue).Count)"
Write-Host "Augmented: $((Get-ChildItem output/augmented/images/*.png -ErrorAction SilentlyContinue).Count)"
Write-Host "Mosaics: $((Get-ChildItem output/mosaics/images/*.png -ErrorAction SilentlyContinue).Count)"
```

---

## 🔧 PHASE 2: MISE À JOUR DES SCRIPTS (1-2h)

### 2.1: Scripts Core (45 min)

#### `core/mosaic.py` (PRIORITÉ 1)
```python
# LIGNE 45-51
# AVANT:
FAKE_DIR = "fakeimg_augmented"
YOLO_OUTPUT_DIR = os.path.join("output", "yolov8")
YOLO_IMAGES_DIR = os.path.join(YOLO_OUTPUT_DIR, "images")
YOLO_LABELS_DIR = os.path.join(YOLO_OUTPUT_DIR, "labels")

# APRÈS:
FAKE_DIR = os.path.join("backgrounds", "augmented")
MOSAIC_OUTPUT_DIR = os.path.join("output", "mosaics")
MOSAIC_IMAGES_DIR = os.path.join(MOSAIC_OUTPUT_DIR, "images")
MOSAIC_LABELS_DIR = os.path.join(MOSAIC_OUTPUT_DIR, "labels")

# LIGNE 391 et 395 (renommer variables)
layout_path = os.path.join(MOSAIC_IMAGES_DIR, layout_filename)
label_path = os.path.join(MOSAIC_LABELS_DIR, label_filename)

# LIGNE 474 (data.yaml)
yaml_path = os.path.join(MOSAIC_OUTPUT_DIR, "data.yaml")
```

#### `core/augmentation.py` (PRIORITÉ 2)
```python
# LIGNE 40 (ajouter option source)
parser.add_argument("--source", type=str, default="images", 
                    choices=["images", "holographic"],
                    help="Source des images à augmenter")

# LIGNE 51-57 (adapter selon source)
BASE_IMAGES_DIR = "output/holographic" if args.source == "holographic" else "images"
# Le reste inchangé (output/augmented reste le même)
```

#### `core/holographic_augmenter.py` (PRIORITÉ 3)
```python
# LIGNE 286 (rendre output optionnel avec défaut)
parser.add_argument("--output", default="output/holographic", 
                    help="Dossier de sortie")
```

#### `core/random_erasing.py` (PRIORITÉ 4)
```python
# LIGNE 97
parser.add_argument("--output_dir", type=str, default="backgrounds/augmented",
                    help="Dossier de sortie")
```

#### `core/workflow_manager.py` (PRIORITÉ 5)
```python
# LIGNE 77-78
output_dir: Path = Path("output")
dataset_dir: Path = Path("output/dataset")  # Renommé de yolo_dir
```

#### `core/training_manager.py` (PRIORITÉ 6)
```python
# LIGNE ~73 (chercher data_yaml)
data_yaml: Path = Path("output/dataset/data.yaml")  # Changé de output/yolov8
```

#### `core/auto_balancer.py` (PRIORITÉ 7)
```python
# Si utilisé, pointer vers dataset
# Dans __init__ ou main(), utiliser Path("output/dataset")
```

#### `check_corrupted_images.py` (PRIORITÉ 8)
```python
# LIGNE 4
img_dir = Path('output/dataset/images')  # Changé de output/yolov8/images
```

### 2.2: GUI et Config (30 min)

#### `GUI_v3.1_modern.py`

**LIGNE 67-69** (defaults):
```python
self.default_output_dir = tk.StringVar(value=config.get("default_output_dir", "output"))
self.default_holographic_dir = tk.StringVar(value=config.get("default_holographic_dir", "output/holographic"))
self.default_augmented_dir = tk.StringVar(value=config.get("default_augmented_dir", "output/augmented"))
self.default_mosaic_dir = tk.StringVar(value=config.get("default_mosaic_dir", "output/mosaics"))
self.default_dataset_dir = tk.StringVar(value=config.get("default_dataset_dir", "output/dataset"))
self.default_fakeimg_dir = tk.StringVar(value=config.get("default_fakeimg_dir", "backgrounds/augmented"))
```

**Dans `save_settings()`** (ajouter):
```python
"default_dataset_dir": self.default_dataset_dir.get(),
"default_holographic_dir": self.default_holographic_dir.get(),
```

**Dans `create_general_tab()`** (ajouter nouveau champ):
```python
# Après Mosaic directory
tk.Label(container, text="📦 Dataset Final Directory:", ...)
frame_dataset = tk.Frame(...)
tk.Entry(frame_dataset, textvariable=self.default_dataset_dir, ...)
```

#### `gui_config.json`

Remplacer **entièrement** la section `"paths"` et `"defaults"`:
```json
{
    "paths": {
        "images_source": "images",
        "backgrounds": "backgrounds",
        "backgrounds_augmented": "backgrounds/augmented",
        "output_holographic": "output/holographic",
        "output_augmented": "output/augmented",
        "output_mosaics": "output/mosaics",
        "output_dataset": "output/dataset",
        "excel_file": "excel/cards_info.xlsx"
    },
    "defaults": {
        "images_dir": "images",
        "output_dir": "output",
        "holographic_dir": "output/holographic",
        "augmented_dir": "output/augmented",
        "mosaic_dir": "output/mosaics",
        "dataset_dir": "output/dataset",
        "backgrounds_dir": "backgrounds",
        "backgrounds_augmented_dir": "backgrounds/augmented",
        "fakeimg_dir": "backgrounds/augmented",
        "augmentations": 15,
        ...
    }
}
```

---

## ✅ PHASE 3: VALIDATION (30 min)

### 3.1: Tests unitaires par script

```powershell
# Test holographic
python core/holographic_augmenter.py images --output output/holographic
# Vérifier: output/holographic/images/ contient les images

# Test augmentation
python core/augmentation.py --num_aug 5 --target augmented
# Vérifier: output/augmented/images/ contient les augmentations

# Test mosaic
python core/mosaic.py 1 0 0 --max-groups 10
# Vérifier: output/mosaics/images/ contient les mosaïques

# Test merge
python merge_dataset.py
# Vérifier: output/dataset/ contient tout
```

### 3.2: Test workflow complet

```powershell
# Clean test
Remove-Item output/holographic, output/augmented, output/mosaics, output/dataset -Recurse -ErrorAction SilentlyContinue

# Workflow complet
python core/holographic_augmenter.py images --output output/holographic
python core/augmentation.py --num_aug 150
python core/mosaic.py 1 0 0 --max-groups 150
python merge_dataset.py

# Vérifier dataset final
Get-ChildItem output/dataset/images | Measure-Object
Get-ChildItem output/dataset/labels | Measure-Object
```

### 3.3: Test GUI

```powershell
python GUI_v3.1_modern.py
# Vérifier dans Settings:
# - Tous les chemins pointent vers les nouveaux répertoires
# - Les chemins sont sauvegardés correctement
# - Les workflows fonctionnent
```

---

## 📊 CHECKLIST DE VALIDATION

### Données
- [ ] Images originales intactes dans `images/`
- [ ] Backgrounds dans `backgrounds/original/` et `backgrounds/augmented/`
- [ ] Holographiques dans `output/holographic/`
- [ ] Augmentées dans `output/augmented/`
- [ ] Mosaïques dans `output/mosaics/`
- [ ] Dataset final dans `output/dataset/`

### Scripts Core
- [ ] `core/mosaic.py` → utilise `output/mosaics/`
- [ ] `core/augmentation.py` → utilise `output/augmented/`
- [ ] `core/holographic_augmenter.py` → utilise `output/holographic/`
- [ ] `core/random_erasing.py` → utilise `backgrounds/augmented/`
- [ ] `core/workflow_manager.py` → utilise `output/dataset/`
- [ ] `core/training_manager.py` → utilise `output/dataset/data.yaml`
- [ ] `check_corrupted_images.py` → utilise `output/dataset/`

### GUI
- [ ] Settings dialog affiche tous les nouveaux chemins
- [ ] Chemins par défaut corrects dans `gui_config.json`
- [ ] Sauvegarde des settings fonctionne
- [ ] Workflows utilisent les nouveaux chemins

### Fonctionnel
- [ ] Génération holographique OK
- [ ] Génération augmentation OK
- [ ] Génération mosaïques OK
- [ ] Fusion dataset OK
- [ ] Entraînement YOLO OK (test rapide 5 epochs)

---

## 🚨 POINTS D'ATTENTION

1. **Backup OBLIGATOIRE** avant toute modification
2. **Tester chaque script** après modification
3. **Ne pas supprimer** `output/yolov8/` avant validation complète
4. **Garder le backup** 48h minimum
5. **Documenter** tout problème rencontré

---

## 📞 EN CAS DE PROBLÈME

### Restauration backup
```powershell
$backup = "backup_YYYYMMDD_HHMMSS"  # Remplacer par nom réel
Remove-Item output, augment, backgrounds -Recurse -ErrorAction SilentlyContinue
Copy-Item -Recurse "$backup/*" .
```

### Logs de debug
```powershell
# Activer logs verbeux
$env:DEBUG=1
python core/mosaic.py 1 0 0 --max-groups 10 > test_mosaic.log 2>&1
```

---

## 🎯 RÉSULTAT ATTENDU

- ✅ Structure claire et logique
- ✅ Chaque étape du pipeline isolée
- ✅ Pas de doublons ni confusion
- ✅ Tous les scripts cohérents
- ✅ Dataset final prêt pour training
- ✅ Maintenance facilitée

---

## 📚 DOCUMENTATION

- `ANALYSE_REPERTOIRES.md` : Analyse complète
- `migrate_directories.py` : Script de migration automatique
- `merge_dataset.py` : Script de fusion du dataset
- `migration_report.txt` : Rapport généré après migration

---

**Temps total estimé : 2-3 heures**
- Phase 1 (Migration) : 1h
- Phase 2 (Scripts) : 1-2h  
- Phase 3 (Validation) : 30min
