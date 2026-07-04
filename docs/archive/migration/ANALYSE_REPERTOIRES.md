# 📊 ANALYSE COMPLÈTE DES RÉPERTOIRES - Pokémon Dataset Generator

## 🎯 Objectif
Réorganiser tous les répertoires de sortie pour une structure **claire, cohérente et maintenable**.

---

## 📁 STRUCTURE ACTUELLE (Problématique)

```
pok/
├── images/                    # ✅ SOURCE OK
├── augment/                   # ⚠️ Holographic temporaire
├── fakeimg/                   # ⚠️ Backgrounds originaux
├── fakeimg_augmented/         # ⚠️ Backgrounds augmentés
├── output/
│   ├── augmented/             # ⚠️ Augmentations standard
│   │   ├── images/ (1200)
│   │   └── labels/ (1200)
│   ├── yolov8/                # ⚠️ Mélange augmented + mosaics
│   │   ├── images/ (1350)    # 1200 augmented + 150 mosaics
│   │   └── labels/ (1350)
│   └── yolov8_test/           # ❌ DOUBLON inutile
│       ├── images/ (1200)
│       └── labels/ (1200)
└── runs/                      # ✅ YOLO training OK
```

### ❌ Problèmes Identifiés

1. **Confusion de noms**
   - `augment/` vs `output/augmented/` : Lequel est quoi ?
   - `fakeimg/` vs `fakeimg_augmented/` : Quelle différence ?

2. **Mélange de données**
   - `output/yolov8/images/` : Contient augmentations + mosaïques
   - Impossible de distinguer les types de fichiers

3. **Doublons**
   - `output/yolov8_test/` : Copie inutile de `augmented/`

4. **Manque de traçabilité**
   - Difficile de suivre le pipeline : source → holo → augment → mosaic → dataset

5. **Incohérence dans les scripts**
   - Chaque script utilise des chemins différents
   - Hardcodés partout : `output/yolov8`, `augmented`, etc.

---

## 📁 STRUCTURE PROPOSÉE (Solution)

```
pok/
├── images/                          # 🔵 SOURCE : 8 cartes originales
│   └── sv08_XXX.png
│
├── backgrounds/                     # 🟣 BACKGROUNDS (renommé de fakeimg/)
│   ├── original/                    # Backgrounds originaux
│   └── augmented/                   # Backgrounds augmentés (random erasing)
│
├── output/                          # 🔴 TOUS LES OUTPUTS DU PIPELINE
│   │
│   ├── holographic/                 # Étape 1 : Augmentation holographique
│   │   ├── images/ (24)            # 8 cartes × 3 variants
│   │   └── labels/ (24)
│   │
│   ├── augmented/                   # Étape 2 : Augmentation standard
│   │   ├── images/ (1200)          # 8 × 150 variants
│   │   └── labels/ (1200)
│   │
│   ├── mosaics/                     # Étape 3 : Génération mosaïques
│   │   ├── images/ (150-250)       # Mosaïques uniquement
│   │   └── labels/ (150-250)
│   │
│   └── dataset/                     # Étape 4 : DATASET FINAL YOLO
│       ├── images/                  # TOUTES les images (augmented + mosaics)
│       ├── labels/                  # TOUS les labels
│       ├── train.txt                # Liste des fichiers train (80%)
│       ├── val.txt                  # Liste des fichiers validation (20%)
│       └── data.yaml                # Configuration YOLO
│
├── runs/                            # 🟢 RÉSULTATS ENTRAÎNEMENT (inchangé)
│   └── train/
│       └── pokemon_detector/
│
└── bbox_visualization/              # 🟡 VALIDATION (temporaire, inchangé)
```

---

## 🔄 WORKFLOW CLAIR

```
┌─────────┐
│ images/ │  (8 cartes originales)
└────┬────┘
     │
     ↓ holographic_augmenter.py
     │
┌────────────────────┐
│ output/holographic/ │  (24 images)
└─────────┬──────────┘
          │
          ↓ augmentation.py --source holographic
          │
┌─────────────────────┐
│ output/augmented/    │  (1200 images)
└─────────┬───────────┘
          │
          ↓ mosaic.py --input augmented
          │
┌─────────────────────┐
│ output/mosaics/      │  (150-250 mosaics)
└─────────┬───────────┘
          │
          ↓ merge_dataset.py
          │
┌─────────────────────┐
│ output/dataset/      │  (Dataset final YOLO)
└─────────┬───────────┘
          │
          ↓ yolo train data=output/dataset/data.yaml
          │
┌─────────────────────┐
│ runs/train/          │  (Résultats entraînement)
└─────────────────────┘
```

---

## 📝 FICHIERS À MODIFIER

### 1. Core Scripts (8 fichiers)

#### `core/holographic_augmenter.py`
```python
# AVANT
parser.add_argument("output", help="Dossier de sortie")

# APRÈS
parser.add_argument("--output", default="output/holographic", help="Dossier de sortie")
```

#### `core/augmentation.py`
```python
# AVANT
BASE_IMAGES_DIR = "images"
AUG_OUTPUT_DIR = os.path.join("output", "augmented")

# APRÈS
parser.add_argument("--source", default="images", choices=["images", "holographic"])
BASE_IMAGES_DIR = "output/holographic" if args.source == "holographic" else "images"
AUG_OUTPUT_DIR = os.path.join("output", "augmented")  # Inchangé
```

#### `core/mosaic.py`
```python
# AVANT
INPUT_DIRS = [os.path.join("output", "augmented", "images")]
FAKE_DIR = "fakeimg_augmented"
YOLO_OUTPUT_DIR = os.path.join("output", "yolov8")
YOLO_IMAGES_DIR = os.path.join(YOLO_OUTPUT_DIR, "images")
YOLO_LABELS_DIR = os.path.join(YOLO_OUTPUT_DIR, "labels")

# APRÈS
INPUT_DIRS = [os.path.join("output", "augmented", "images")]
FAKE_DIR = os.path.join("backgrounds", "augmented")
MOSAIC_OUTPUT_DIR = os.path.join("output", "mosaics")
MOSAIC_IMAGES_DIR = os.path.join(MOSAIC_OUTPUT_DIR, "images")
MOSAIC_LABELS_DIR = os.path.join(MOSAIC_OUTPUT_DIR, "labels")
```

#### `core/workflow_manager.py`
```python
# AVANT
output_dir: Path = Path("output")
yolo_dir: Path = Path("output/yolov8")

# APRÈS
output_dir: Path = Path("output")
dataset_dir: Path = Path("output/dataset")
```

#### `core/auto_balancer.py`
```python
# AVANT (pas de changement majeur, mais pointer vers dataset/)
# dataset_dir = Path("output/yolov8")

# APRÈS
dataset_dir = Path("output/dataset")
```

#### `core/training_manager.py`
```python
# AVANT
data_yaml: Path = Path("output/yolov8/data.yaml")

# APRÈS
data_yaml: Path = Path("output/dataset/data.yaml")
```

#### `core/random_erasing.py`
```python
# AVANT
parser.add_argument("--output_dir", type=str, default="fakeimg_augmented")

# APRÈS
parser.add_argument("--output_dir", type=str, default="backgrounds/augmented")
```

#### `check_corrupted_images.py`
```python
# AVANT
img_dir = Path('output/yolov8/images')

# APRÈS
img_dir = Path('output/dataset/images')
```

---

### 2. GUI Files (2 fichiers)

#### `GUI_v3.1_modern.py`
**Lignes 67-69** : Defaults
```python
# AVANT
self.default_output_dir = tk.StringVar(value=config.get("default_output_dir", "output"))
self.default_augmented_dir = tk.StringVar(value=config.get("default_augmented_dir", "augmented"))
self.default_mosaic_dir = tk.StringVar(value=config.get("default_mosaic_dir", "output/yolov8"))

# APRÈS
self.default_output_dir = tk.StringVar(value=config.get("default_output_dir", "output"))
self.default_augmented_dir = tk.StringVar(value=config.get("default_augmented_dir", "output/augmented"))
self.default_mosaic_dir = tk.StringVar(value=config.get("default_mosaic_dir", "output/mosaics"))
self.default_dataset_dir = tk.StringVar(value=config.get("default_dataset_dir", "output/dataset"))
```

**Ajouter** : Nouveau champ dans Settings
```python
# Dans create_general_tab()
tk.Label(..., text="📦 Dataset Final Directory:")
tk.Entry(..., textvariable=self.default_dataset_dir)
```

#### `gui_config.json`
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
        ...
    }
}
```

---

### 3. Batch Files (optionnel, 2 fichiers)

#### `tools/test_mosaic.bat`
```bat
REM AVANT
if exist output\yolov8\images (

REM APRÈS
if exist output\mosaics\images (
```

---

## 🆕 NOUVEAU SCRIPT : `merge_dataset.py`

**Objectif** : Fusionner `output/augmented/` + `output/mosaics/` → `output/dataset/`

```python
#!/usr/bin/env python3
"""
Fusionne les images augmentées et les mosaïques dans un dataset YOLO final
"""
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split

def merge_dataset():
    # Chemins source
    augmented_dir = Path("output/augmented")
    mosaics_dir = Path("output/mosaics")
    dataset_dir = Path("output/dataset")
    
    # Créer structure dataset
    (dataset_dir / "images").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "labels").mkdir(parents=True, exist_ok=True)
    
    # Copier augmented
    for img in (augmented_dir / "images").glob("*.png"):
        shutil.copy(img, dataset_dir / "images" / img.name)
    for lbl in (augmented_dir / "labels").glob("*.txt"):
        shutil.copy(lbl, dataset_dir / "labels" / lbl.name)
    
    # Copier mosaics
    for img in (mosaics_dir / "images").glob("*.png"):
        shutil.copy(img, dataset_dir / "images" / img.name)
    for lbl in (mosaics_dir / "labels").glob("*.txt"):
        shutil.copy(lbl, dataset_dir / "labels" / lbl.name)
    
    # Créer train/val split
    all_images = list((dataset_dir / "images").glob("*.png"))
    train_imgs, val_imgs = train_test_split(all_images, test_size=0.2, random_state=42)
    
    with open(dataset_dir / "train.txt", "w") as f:
        f.write("\n".join([str(img.relative_to(dataset_dir)) for img in train_imgs]))
    
    with open(dataset_dir / "val.txt", "w") as f:
        f.write("\n".join([str(img.relative_to(dataset_dir)) for img in val_imgs]))
    
    # Copier/créer data.yaml
    shutil.copy(augmented_dir / "data.yaml", dataset_dir / "data.yaml")
    
    print(f"✅ Dataset final créé:")
    print(f"   Total: {len(all_images)} images")
    print(f"   Train: {len(train_imgs)} | Val: {len(val_imgs)}")

if __name__ == "__main__":
    merge_dataset()
```

---

## ✅ AVANTAGES DE LA NOUVELLE STRUCTURE

1. **Clarté** : Chaque étape a son dossier dédié
2. **Traçabilité** : Pipeline visible : holo → augmented → mosaics → dataset
3. **Séparation** : Plus de mélange augmented/mosaics
4. **Maintenabilité** : Facile de régénérer une étape spécifique
5. **Nettoyage** : `rm -rf output/` supprime tout sauf sources
6. **Consistance** : Tous les scripts utilisent les mêmes chemins
7. **Extensibilité** : Facile d'ajouter de nouvelles étapes

---

## 📋 CHECKLIST DE MIGRATION

### Phase 1 : Backup
- [ ] Sauvegarder `output/` → `output_backup/`
- [ ] Sauvegarder `augment/` → `augment_backup/`
- [ ] Sauvegarder `fakeimg*` → `fakeimg_backup/`

### Phase 2 : Création structure
- [ ] Créer `backgrounds/original/`
- [ ] Créer `backgrounds/augmented/`
- [ ] Créer `output/holographic/`
- [ ] Créer `output/mosaics/`
- [ ] Créer `output/dataset/`

### Phase 3 : Migration données
- [ ] Déplacer `fakeimg/` → `backgrounds/original/`
- [ ] Déplacer `fakeimg_augmented/` → `backgrounds/augmented/`
- [ ] Déplacer `augment/` → `output/holographic/`
- [ ] Copier mosaics de `output/yolov8/images/layout_*.png` → `output/mosaics/`
- [ ] Supprimer `output/yolov8_test/`

### Phase 4 : Mise à jour scripts
- [ ] `core/holographic_augmenter.py`
- [ ] `core/augmentation.py`
- [ ] `core/mosaic.py`
- [ ] `core/workflow_manager.py`
- [ ] `core/auto_balancer.py`
- [ ] `core/training_manager.py`
- [ ] `core/random_erasing.py`
- [ ] `check_corrupted_images.py`

### Phase 5 : Mise à jour GUI
- [ ] `GUI_v3.1_modern.py` (defaults)
- [ ] `gui_config.json`

### Phase 6 : Création nouveaux outils
- [ ] Créer `merge_dataset.py`
- [ ] Créer `migrate_directories.py` (script de migration automatique)

### Phase 7 : Validation
- [ ] Tester workflow complet
- [ ] Vérifier tous les chemins
- [ ] Tester GUI
- [ ] Régénérer dataset de test

---

## 🚀 PROCHAINES ÉTAPES

1. **Créer script de migration automatique** (`migrate_directories.py`)
2. **Valider avec utilisateur** : Structure OK ?
3. **Exécuter migration**
4. **Mettre à jour tous les scripts** (8 fichiers core + 2 GUI)
5. **Tester workflow complet**
6. **Nettoyer backups** si tout fonctionne
