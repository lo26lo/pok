# ✨ Features - Pokémon Dataset Generator

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025

---

## 📋 Vue d'Ensemble

Le **Pokémon Dataset Generator** est une application complète pour créer, entraîner et déployer des modèles de détection de cartes Pokémon avec YOLO.

**Pipeline Complet** :
```
📥 Download → 🎨 Augmentation → 🖼️ Mosaics → ✅ Validation → 🎓 Training → 🔍 Detection
```

---

## 🎨 1. Interface Graphique (GUI v3.2)

### Design Moderne
- ✅ **Catppuccin Mocha** : Palette de couleurs professionnelle
- ✅ **Architecture 3 zones** : Header, Sidebar, Main Content
- ✅ **Sidebar collapsible** : Maximise espace de travail
- ✅ **Dark theme** : Confort visuel prolongé

### 11 Vues Fonctionnelles

| Vue | Fonction | Raccourci |
|-----|----------|-----------|
| 🏠 **Home** | Dashboard temps réel | Ctrl+H |
| 🔄 **Workflow** | Pipeline automatique | Ctrl+W |
| 📥 **Download** | TCGdex API images | Ctrl+D |
| 🎨 **Augmentation** | 22 techniques imgaug | Ctrl+A |
| 💎 **Fake Images** | Backgrounds générés | Ctrl+F |
| 🖼️ **Mosaics** | Compositions annotées | Ctrl+M |
| ✅ **Validation** | 5 checks qualité | Ctrl+V |
| 🎓 **Training** | YOLOv8/v11 | Ctrl+T |
| 🔍 **Detection** | Temps réel | Ctrl+R |
| 📦 **Export** | 4 formats | Ctrl+E |
| 🔧 **Tools** | Utilitaires | Ctrl+U |

### Dashboard (Home)

**4 Stats Cards Temps Réel** :
- 📊 **Total Images** : Compteur images téléchargées
- 🎨 **Augmented Images** : Images générées par augmentation
- 🖼️ **Mosaics Generated** : Mosaïques créées
- 🎯 **Training Runs** : Nombre d'entraînements

**Quick Actions** (4 boutons) :
- ▶️ **Start Workflow** : Lance pipeline complet
- 📥 **Download Images** : Ouvre vue Download
- 🎓 **Train Model** : Ouvre vue Training
- 🔍 **Run Detection** : Ouvre vue Detection

**Environment Status** :
- 🐍 Python version (3.10/3.11/3.12)
- 🎮 GPU détecté (CUDA/ROCm/MPS/None)
- 💾 VRAM disponible (si GPU)

**Auto-Refresh** : Stats mises à jour toutes les 5 sec

---

## 🔄 2. Workflow Automatique

### Pipeline 5 Étapes

**Configuration** :
```python
WorkflowConfig(
    input_dir="images/surging_sparks",
    num_augmentations=5,
    mosaic_mode="standard",
    enable_holographic=True,
    enable_validation=True,
    enable_auto_balance=True,
    enable_training=False  # Optionnel
)
```

**Étapes** :
1. **Augmentation** (30-60 min) : 22 techniques imgaug
2. **Holographic** (5-10 min, optionnel) : 5 styles
3. **Mosaics** (5-15 min) : Compositions 640×640
4. **Validation + Balance** (10-20 min) : Checks + équilibrage
5. **Training** (2-8h, optionnel) : YOLOv8/v11

**Durée Totale** : 1-2h (sans training), 3-10h (avec training)

**Use Cases** :
- ✅ **Quick Test** : 50 cartes, mode Quick → 1h
- ✅ **Production** : 500 cartes, mode Complete → 4-6h
- ✅ **Competition** : 1000 cartes, training complet → 8-12h

---

## 📥 3. Téléchargement d'Images (TCGdex API)

### TCGdex v2 API Integration

**10 Langues Supportées** :
- 🇬🇧 English (en)
- 🇫🇷 Français (fr)
- 🇩🇪 Deutsch (de)
- 🇪🇸 Español (es)
- 🇮🇹 Italiano (it)
- 🇵🇹 Português (pt)
- 🇯🇵 日本語 (ja)
- 🇰🇷 한국어 (ko)
- 🇹🇼 中文 (zh-tw)
- 🇵🇱 Polski (pl)

**13+ Sets Populaires** :
- Surging Sparks (sv08)
- Obsidian Flames (sv03)
- Paldea Evolved (sv02)
- Scarlet & Violet (sv01)
- Crown Zenith (swsh12.5)
- Silver Tempest (swsh12)
- Lost Origin (swsh11)
- ...

**Features** :
- ✅ Parallel downloads (5 threads)
- ✅ Retry automatique (3 tentatives)
- ✅ Progression temps réel
- ✅ Haute résolution (512×710 pixels)

**Performance** :
- 200 cartes : 5-10 min
- 500 cartes : 15-25 min

---

## 🎨 4. Augmentation Avancée

### 22 Techniques imgaug

**Couleur (4)** :
- Brightness (-50 à +50)
- Contrast (0.5-1.5)
- Saturation (0.5-1.5)
- Hue (-30 à +30)

**Blur/Sharpen (3)** :
- Gaussian Blur (σ 0-2)
- Sharpen (α 0-1)
- Motion Blur (kernel 3-7)

**Noise (3)** :
- Gaussian Noise (0-3%)
- Dropout (0-5%)
- Coarse Dropout (0-10%)

**Géométrique (6)** :
- Rotation (±15°)
- Affine (scale, translate, shear)
- Perspective (0-5%)
- Elastic Transform (α 0-30)
- Piecewise Affine (0-3%)
- Flip Horizontal (50%)

**Autres (6)** :
- CLAHE (clip 1-4)
- Cutout (0-3 rectangles)
- Random Erasing (prob 0.5)
- +3 autres

**Configuration** :
- Count : 1-20 augmentations/image
- Techniques : Activable individuellement
- Random order : Ordre aléatoire application

**Performance** :
- CPU : 2-5 sec/image
- GPU : imgaug GPU expérimental (désactivé)

---

## ✨ 5. Effets Holographiques

### 5 Styles Disponibles

**1. Rainbow** 🌈
- Arc-en-ciel multicolore
- HSV hue shift
- Intensité : 0.1-1.0

**2. Metallic** 🔩
- Reflets métalliques argentés
- Gradients radiaux
- GPU accelerated

**3. Glitter** ✨
- Paillettes scintillantes
- Noise haute-fréquence
- Sparkles blancs

**4. Prismatic** 💎
- Prismes chromatiques
- Aberration chromatic
- Multi-couleurs

**5. Sparkle** ⭐
- Étoiles brillantes
- Star patterns
- Effet magique

**Performance v3.2.2 (optimisé 100-300×)** :

| Style | Avant | Après | Speedup |
|-------|-------|-------|---------|
| Rainbow | 2.5s | 0.025s | 100× |
| Metallic | 3.0s | 0.01s | 300× |
| Glitter | 1.8s | 0.015s | 120× |

**Usage** : Appliqué après augmentation pour réalisme

---

## 🖼️ 6. Génération de Mosaïques

### 3 Modes de Génération

**1. Quick Mode**
- 2-4 cartes/mosaïque
- Backgrounds simples
- Durée : 1-2 min / 100 mosaïques

**2. Standard Mode** (recommandé)
- 4-6 cartes/mosaïque
- Rotation aléatoire
- Backgrounds variés
- Durée : 5-8 min / 100 mosaïques

**3. Complete Mode**
- 6-8 cartes/mosaïque
- Tous layouts
- Backgrounds complexes
- Durée : 10-15 min / 100 mosaïques

### 3 Layouts

**Grid** : Disposition grille régulière
**Rotation** : Cartes tournées aléatoirement
**Random** : Positions complètement aléatoires

### 3 Types de Backgrounds

**Mosaic** : Fond mosaïque uni
**Local** : Images depuis `backgrounds/`
**Web** : Téléchargement backgrounds en ligne

### Annotations YOLO

**2 Formats** :
- ✅ Bounding boxes (x_center, y_center, width, height)
- ✅ Polygones 4 points (coins de cartes)

**Performance v3.2.1 (optimisé 30-60×)** :

| Configuration | Avant | Après | Speedup |
|---------------|-------|-------|---------|
| 100 Quick | 180s | 6s | 30× |
| 500 Complete | 2400s | 40s | 60× |

---

## 💎 7. Fake Images (Backgrounds)

**But** : Générer backgrounds pour augmenter négatives

**3 Types** :
1. **Perlin Noise** : Bruit organique
2. **Uniform** : Couleur unie
3. **Gradient** : Dégradé linéaire

**Random Erasing** :
- Rectangles aléatoires effacés
- Count : 1-10 erasings
- Area : 2-40% de l'image

**Performance** : 0.05 sec/background

---

## ✅ 8. Validation Dataset

### 5 Checks Automatiques

**1. Image Integrity**
- ❌ Images corrompues
- ❌ Taille < 32×32
- ❌ Format invalide

**2. Label Integrity**
- ❌ Format YOLO invalide
- ❌ Bbox hors [0, 1]
- ❌ Valeurs non parsables

**3. Class Distribution**
- ⚠️ Déséquilibre > 5:1
- 📊 Stats par classe

**4. Annotation Quality**
- ⚠️ Bbox < 1% image
- ⚠️ Overlaps > 80%

**5. Data Consistency**
- ❌ Images sans labels
- ❌ Labels orphelins

**Output** : `validation_report.html` avec erreurs/warnings colorés

---

## ⚖️ 9. Auto-Balancing

### 3 Stratégies

**1. Upsampling**
- Dupliquer classes minoritaires
- Augmenter duplicatas

**2. Downsampling**
- Réduire classes majoritaires
- Échantillonnage aléatoire

**3. Combined** (recommandé)
- Mix des deux stratégies
- Distribution uniforme

**Target Count** :
- Auto : Médiane des counts
- Manuel : Valeur spécifiée

**Performance** :
- Upsampling 500 images : 20-30 min
- Downsampling : 10 sec
- Combined : 25-35 min

---

## 🎓 10. Entraînement YOLO

### Modèles Supportés

**YOLOv8** :
- n (3.2M params) : Production rapide
- s (11.2M) : Équilibre
- m (25.9M) : Précision élevée
- l (43.7M) : Maximum précision
- x (68.2M) : Compétition

**YOLO11** (2024) :
- n (2.6M) : Dernière version
- s (9.4M) : YOLO11 équilibré

### Configuration

**Paramètres** :
- Epochs : 1-1000 (défaut 50)
- Batch size : 1-64 (défaut 16)
- Image size : 320-1280 (défaut 640)
- Device : Auto/CPU/CUDA/MPS
- Workers : 1-32 (défaut 8)

**Optimisations** :
- ✅ Pretrained (COCO transfer learning)
- ✅ Cache (images en RAM)
- ✅ Mixed precision FP16 (2× plus rapide)
- ✅ Early stopping (patience 20 epochs)

### Métriques

**Training** :
- box_loss, cls_loss, dfl_loss

**Validation** :
- Precision, Recall
- mAP50, mAP50-95

**Outputs** :
- `runs/detect/train/weights/best.pt`
- `results.png`, `confusion_matrix.png`
- Courbes F1, PR, etc.

**Durée** :
- 500 images, 50 epochs, RTX 3060 : 2-3h
- 500 images, 50 epochs, CPU : 6-8h

---

## 🔍 11. Détection Temps Réel

### 3 Modes

**1. Webcam** 📹
- Flux caméra temps réel
- FPS : 15-60 (selon GPU)
- Raccourcis : 'q' quit, 's' screenshot

**2. Video File** 🎬
- Traitement vidéo pré-enregistrée
- Output : Vidéo annotée
- Progression frame par frame

**3. Image File** 🖼️
- Détection statique
- Output : Image annotée
- Instantané

### Configuration

**Seuils** :
- Confidence : 0.0-1.0 (défaut 0.25)
- IoU : 0.0-1.0 (défaut 0.45)

**Visualisation** :
- Bounding boxes colorées
- Labels (classe + confidence)
- FPS counter (webcam)

### Système de Prix 💰

**Show Prices** :
- ✅ Overlay prix Cardmarket (EUR)
- ✅ Prix TCGPlayer (USD)
- ✅ Mapping class_id → card → prix

**Base de Données** :
- `models/cards_database.yaml`
- Initialisation depuis TCGdex API
- Mise à jour manuelle/automatique

**Performance** :
- RTX 3060 + YOLOv8n : 45-60 FPS
- CPU + YOLOv8n : 8-15 FPS

---

## 📦 12. Export Multi-Format

### 4 Formats Supportés

**1. COCO JSON**
- Standard industriel (2014-present)
- TensorFlow, Detectron2, MMDetection
- `instances_train.json`, `instances_val.json`

**2. Pascal VOC XML**
- Format legacy (2005-2012)
- PyTorch, torchvision
- 1 XML par image

**3. TFRecord**
- Format binaire TensorFlow
- Ultra-rapide (lecture optimisée)
- TF Object Detection API

**4. Roboflow**
- Structure YOLO + data.yaml
- Upload direct sur Roboflow.com
- Versioning cloud

### Splits

**Configuration** :
- Train : 70% (défaut)
- Val : 20%
- Test : 10%

**Include Augmented** : Option inclure images augmentées

**Performance** :
- COCO (500 images) : 30-45 sec
- VOC : 45-60 sec
- TFRecord : 60-90 sec
- Roboflow : 20-30 sec

---

## 🔧 13. Outils & Utilitaires

### Excel & Prices Manager
- 📋 Create Excel template
- 🌐 Import from TCGdex
- 🔄 Convert Excel → YAML
- 💰 Update prices

### TCG Browser
- 🌐 Explorer API TCGdex
- 🖼️ Visualiser cartes
- 📥 Télécharger sélection

### Clean & Reset
- 🧹 Clean temp files (cache, pyc)
- 🔄 Reset to defaults (config)
- ⚠️ Deep clean (supprime tout)

### Statistics & Reports
- 📊 Generate project report HTML
- 📦 Create archive backup (.zip)

---

## ⚙️ 14. Settings (8 Tabs)

**1. General** : Langue, thème, auto-save
**2. Augmentation** : Count, techniques defaults
**3. Mosaic** : Mode, layout, background
**4. Training** : Model, epochs, batch, GPU
**5. Detection** : Confidence, IoU, FPS
**6. Export** : Format, splits
**7. Advanced** : Debug, performance, cache
**8. Debug** : Device, workers, logging, profiling

---

## 📊 Récapitulatif Performance

| Feature | Performance | Optimisation |
|---------|-------------|--------------|
| **Mosaics** | 30-60× speedup | v3.2.1 (vectorisation) |
| **Holographic** | 100-300× speedup | v3.2.2 (GPU, LUT) |
| **Downloads** | 5× speedup | Parallel (5 threads) |
| **Augmentation** | 2-5 sec/image | imgaug pipeline |
| **Training** | 2-3h (GPU) | FP16, cache |
| **Detection** | 45-60 FPS (GPU) | YOLOv8n optimisé |

---

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025
