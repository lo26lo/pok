# 📋 CHECKLIST TEST GUI - WORKFLOW COMPLET

## ✅ Configuration mise à jour
- `gui_config.json` : `mosaic_background` = 0 (Fake Cards Background)
- **ACTION REQUISE**: Fermez et relancez la GUI

---

## 🔄 Workflow à tester (dans l'ordre)

### 1️⃣ ONGLET HOLOGRAPHIQUE
- **Images source**: `images/` (8 cartes)
- **Nombre variations**: `3`
- **Script**: `holographic_augmenter_optimized.py` (GPU)
- **Sortie**: `output/holographic/`
- **✓ Attendu**: 24 images (8 × 3 variations)

### 2️⃣ ONGLET AUGMENTATION
- **Source**: `holographic` (sélectionner dans la liste)
- **Nombre augmentations**: `50`
- **Cible**: `augmented`
- **Sortie**: `output/augmented/`
- **✓ Attendu**: 1,200 images (24 × 50)

### 3️⃣ ONGLET MOSAÏQUE ⚠️ CRITIQUE
- **Mode layout**: `1` (Standard)
- **Mode background**: `0` ✅ **Fake Cards Mosaic** (VÉRIFIER !)
- **Mode transform**: `0`
- **Nombre groupes**: `150`
- **Script**: `mosaic_optimized.py` (GPU)
- **Sortie**: `output/mosaics/`
- **✓ Attendu**: 150 mosaïques AVEC backgrounds texturés

### 4️⃣ ONGLET DATASET
- **Sources**: 
  - Images augmentées: `output/augmented/`
  - Mosaïques: `output/mosaics/`
- **Train/Val split**: 80/20
- **Sortie**: `output/dataset/`
- **✓ Attendu**: 
  - 1,350 images totales
  - 1,080 train images
  - 270 val images
  - 8 classes (300 instances chacune)

---

## ⚠️ Points critiques à vérifier

### Avant de lancer les mosaïques:
- ✓ Mode background = **0** (pas 1 ou 2)
- ✓ Backgrounds disponibles dans `backgrounds/augmented/` (352 fichiers)
- ✓ Script optimisé GPU utilisé

### Après génération des mosaïques:
1. Ouvrir une image dans `output/mosaics/images/`
2. Vérifier qu'elle a un **background texturé** (pas blanc)
3. Vérifier 8 cartes visibles

### Après fusion dataset:
1. Aller dans `output/dataset/visualizations/`
2. Vérifier les bounding boxes sur une mosaïque
3. Vérifier les class_id corrects :
   - sv08_019 → Class 18 (Ho-Oh)
   - sv08_020 → Class 19 (Castform_Sunny_Form)
   - sv08_026 → Class 25 (Oricorio)
   - sv08_046 → Class 45 (Shellos)
   - sv08_051 → Class 50 (Quaxwell)
   - sv08_126 → Class 125 (Bronzor)
   - sv08_132 → Class 131 (Iron_Crown)
   - sv08_152 → Class 151 (Rufflet)

---

## 🚀 Si tout est OK

Le dataset est prêt pour l'entraînement :
```bash
python core/training_manager.py --epochs 50 --batch 16
```

---

## 🔧 En cas de problème

### Mosaïques avec fond blanc:
- Vérifier que background_mode = 0 dans l'interface
- Vérifier `backgrounds/augmented/` non vide
- Relancer uniquement les mosaïques

### Class_id incorrects:
- Le bug mosaic_optimized.py a été corrigé (ligne 94: int(number) - 1)
- Régénérer mosaïques et dataset

### Performances lentes:
- S'assurer que les scripts *_optimized.py sont utilisés
- Vérifier GPU activé (RTX 5070)
