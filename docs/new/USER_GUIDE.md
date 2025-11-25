# 📖 Pokémon Dataset Generator - Guide Utilisateur Complet

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025  
**Application** : GUI_v3.1_modern.py

---

## 📋 Table des Matières

### 🚀 Démarrage
1. [Installation](#1--installation)
2. [Premier Lancement](#2--premier-lancement)
3. [Interface Overview](#3--interface-overview)

### 🎯 Vues Principales (11 vues)
4. [Dashboard (Home)](#4--dashboard-home)
5. [Workflow Automatique](#5--workflow-automatique)
6. [Image Download](#6--image-download)
7. [Augmentation](#7--augmentation)
8. [Effets Holographiques](#8--effets-holographiques)
9. [Génération de Mosaïques](#9--génération-de-mosaïques)
10. [Fake Images (Backgrounds)](#10--fake-images-backgrounds)
11. [Validation Dataset](#11--validation-dataset)
12. [Auto-Balancing](#12--auto-balancing)
13. [Entraînement YOLO](#13--entraînement-yolo)
14. [Détection Live](#14--détection-live)
15. [Export Datasets](#15--export-datasets)
16. [Outils & Utilitaires](#16--outils--utilitaires)

### ⚙️ Configuration
17. [Settings - 8 Tabs Détaillés](#17--settings---8-tabs-détaillés)
18. [Fichiers de Configuration](#18--fichiers-de-configuration)

### ❓ Support
19. [FAQ & Troubleshooting](#19--faq--troubleshooting)
20. [Cas d'Usage Courants](#20--cas-dusage-courants)

---

# 🚀 DÉMARRAGE

## 1. 📦 Installation

### Prérequis

#### Système d'exploitation
- **Windows 10** ou **Windows 11** (testé et validé)
- **Linux/macOS** : Compatible mais non testé officiellement

#### Python
- **Version recommandée** : **Python 3.12**
- **Versions supportées** : Python 3.10, 3.11, 3.12
- ⚠️ **Version interdite** : Python 3.13+ (incompatibilité NumPy 1.x)

**Vérifier votre version Python** :
```batch
python --version
```

#### Matériel
- **RAM** : 4 GB minimum, 8 GB recommandé
- **Disque** : 10 GB d'espace libre (datasets + modèles)
- **GPU** : Optionnel mais recommandé pour l'entraînement
  - NVIDIA GPU avec CUDA 11.8+ ou CUDA 12.4+ (RTX série)
  - Minimum 4 GB VRAM (6 GB+ recommandé)
- **Webcam** : Optionnelle pour détection live

### Installation Automatique (Recommandé)

#### Étape 1 : Télécharger le Projet

**Option A : Git Clone**
```batch
git clone https://github.com/lo26lo/pok.git
cd pok
```

**Option B : Téléchargement ZIP**
1. Télécharger depuis GitHub : `Code` → `Download ZIP`
2. Extraire dans `C:\DATA\pok\` (ou autre emplacement)
3. Ouvrir un terminal dans le dossier

#### Étape 2 : Exécuter l'Installeur

```batch
INSTALL.bat
```

**Ce que fait l'installeur** :
1. ✅ Vérifie la version Python (3.10-3.12)
2. ✅ Crée un environnement virtuel `.venv`
3. ✅ Met à jour `pip`, `setuptools`, `wheel`
4. ✅ Installe toutes les dépendances depuis `config/requirements.txt`
5. ✅ Vérifie la compatibilité NumPy < 2.0
6. ✅ Détecte et configure PyTorch (GPU ou CPU)
7. ✅ Crée les dossiers de sortie (`output/`, `models/`, etc.)
8. ✅ Affiche un rapport de succès

**Durée estimée** : 5-15 minutes (selon connexion Internet)

#### Étape 3 : Lancer l'Application

```batch
START.bat
```

L'application GUI se lance automatiquement !

### Installation Manuelle (Avancée)

Si vous préférez contrôler chaque étape :

```batch
# 1. Créer environnement virtuel
python -m venv .venv

# 2. Activer l'environnement
.venv\Scripts\activate.bat

# 3. Mettre à jour pip
python -m pip install --upgrade pip setuptools wheel

# 4. Installer dépendances
pip install -r config\requirements.txt

# 5. Vérifier installation
python -c "import cv2, albumentations, ultralytics; print('✅ OK')"

# 6. Lancer GUI
python GUI_v3.1_modern.py
```

### Vérification de l'Installation

**Test rapide** :
```batch
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

**Sortie attendue** :
```
PyTorch: 2.1.0+cu118  (ou cu124 selon GPU)
CUDA: True  (si GPU détecté)
```

### Dépendances Principales

| Package | Version | Rôle |
|---------|---------|------|
| **Python** | 3.10-3.12 | Langage de base |
| **NumPy** | >= 1.24.0 | Calculs numériques |
| **OpenCV** | >= 4.8.0 | Traitement d'images |
| **Albumentations** | >= 1.3.0 | Augmentation avancée (30-50% plus rapide) |
| **PyTorch** | 2.0+ | Deep learning framework |
| **Ultralytics** | 8.0+ | YOLOv8/v11 |
| **tkinter** | (inclus Python) | Interface GUI |
| **Pillow** | Latest | Manipulation images |
| **PyYAML** | Latest | Lecture YAML |
| **requests** | Latest | API TCGdex |

**Taille totale installée** : ~2.5 GB (avec PyTorch GPU)

---

## 2. 🎬 Premier Lancement

### Lancement via START.bat

```batch
START.bat
```

**Que se passe-t-il ?**
1. ✅ Activation automatique du `.venv`
2. ✅ Vérification de l'environnement
3. ✅ Lancement de `GUI_v3.1_modern.py`
4. ✅ Ouverture de la fenêtre GUI

### Écran de Bienvenue

Au premier lancement, vous verrez :

**🟢 Si tout est OK** :
```
✅ Virtual Environment: Detected (.venv)
✅ Price Database: Found (models/cards_database.yaml)
✅ YOLO Models: yolo11n.pt, yolov8n.pt available
```

**🔴 Si problème détecté** :
```
⚠️ Warning: Virtual environment not found
⚠️ Warning: Price database missing
🔧 Fix Now button available
```

### Correction des Problèmes

Cliquez sur **"Fix Now"** → Lance automatiquement `INSTALL.bat`

OU manuellement :
```batch
# Recréer l'environnement
INSTALL.bat

# Relancer l'application
START.bat
```

### Configuration Initiale Recommandée

1. **Ouvrir Settings** (icône ⚙️ en haut à droite)
2. **Tab General** :
   - Vérifier chemins par défaut
   - Ajuster workers (4-8 recommandé)
3. **Tab Debug** (nouveau v3.2.4) :
   - Device: Auto (recommandé)
   - Log Level: INFO
4. **Sauvegarder** : `Save Settings`

---

## 3. 🎨 Interface Overview

### Design v3.2 Professionnel

L'interface utilise une **palette Catppuccin Mocha** avec :
- 🌑 **Fond sombre** : `#1e1e2e` (repose les yeux)
- 🔵 **Accent bleu** : `#89b4fa` (actions principales)
- 🟢 **Success vert** : `#a6e3a1` (validations)
- 🔴 **Error rouge** : `#f38ba8` (alertes)
- ⚪ **Champs blancs** : Fond blanc + texte foncé (lisibilité optimale)

### Architecture 3 Zones

```
┌─────────────────────────────────────────────────┐
│  HEADER (Titre + Version + Status + Settings)   │
├──────────┬──────────────────────────────────────┤
│          │                                       │
│ SIDEBAR  │         MAIN CONTENT                  │
│          │                                       │
│ Navigation│    (Vue active : Dashboard,          │
│ 11 vues  │     Augmentation, Training, etc.)     │
│          │                                       │
│          ├───────────────────────────────────────┤
│          │         LOG PANEL                     │
│          │    (Logs temps réel, scrollable)     │
└──────────┴──────────────────────────────────────┘
```

### Header (Barre supérieure)

- **Titre** : "🎮 Pokémon Dataset Generator"
- **Version** : "v3.1 Pro"
- **Status** : "Ready" (🟢) ou "Processing..." (🔵)
- **Settings** : Bouton ⚙️ (ouvre dialog 8 tabs)

### Sidebar (Navigation gauche)

**Sections** :

1. **🏠 MAIN**
   - Dashboard (accueil)

2. **🔄 WORKFLOW**
   - Auto Workflow

3. **📊 DATASET**
   - ⬇️ Image Download
   - 🎨 Augmentation
   - ✨ Holographic
   - 🧩 Mosaics
   - 🖼️ Fake Images

4. **✅ VALIDATION**
   - Validate
   - ⚖️ Auto-Balance

5. **🤖 MODEL**
   - 🎓 Training
   - 🔍 Detection

6. **🛠️ TOOLS**
   - 📦 Export
   - 🔧 Utilities

### Main Content (Zone centrale)

Affiche la **vue active** sélectionnée dans la sidebar.

**Éléments communs** :
- **Titre de la vue** : Ex: "🎨 Augmentation"
- **Subtitle** : Description courte
- **Champs de configuration** : Paramètres de la vue
- **Boutons d'action** : "START", "STOP", "Open Folder"
- **Progress bar** : Barre de progression animée
- **Status** : Message d'état en temps réel

### Log Panel (Bas de l'écran)

**Logs en temps réel** :
- 🟢 `[INFO]` : Informations générales
- 🟡 `[WARNING]` : Avertissements
- 🔴 `[ERROR]` : Erreurs
- 🔵 `[DEBUG]` : Détails techniques (si activé)

**Fonctionnalités** :
- Auto-scroll vers le bas
- Timestamps précis
- Scrollbar pour historique
- Efface automatiquement après 1000 lignes

**Raccourcis** :
- `Ctrl+L` : Effacer les logs
- `Ctrl+S` : Sauvegarder logs dans fichier

---

# 🎯 VUES PRINCIPALES

## 4. 🏠 Dashboard (Home)

Le **Dashboard** est votre centre de contrôle avec statistiques en temps réel.

### Statistiques en Temps Réel

**4 Cartes de stats** :

#### 📂 Source Images
- **Compte** : Nombre d'images originales dans `images/`
- **Format** : PNG, JPG, WEBP supportés
- **Mise à jour** : Automatique toutes les 5 secondes

#### 🎨 Augmented Images
- **Compte** : Images augmentées dans `output/augmented/images/`
- **Ratio** : Affiche multiplication (ex: "×5" si 5 augmentations)
- **Inclut** : Images augmentées + holographiques

#### 🧩 Mosaic Images
- **Compte** : Mosaïques générées dans `output/mosaics/images/`
- **Layouts** : Nombre de dispositions utilisées
- **Annotations** : YOLO labels automatiques

#### 💾 Dataset Size
- **Taille** : Espace disque total utilisé
- **Format** : MB ou GB selon taille
- **Inclut** : Toutes les sorties (augmented + mosaics + runs)

### Quick Actions (Boutons rapides)

4 boutons pour accès directs :

1. **🔄 Run Workflow** → Vue Workflow
2. **🎨 Augment Images** → Vue Augmentation
3. **🧩 Generate Mosaics** → Vue Mosaics
4. **✅ Validate Dataset** → Vue Validation

### Environment Status

**Vérifications système** :

✅ **Virtual Environment**
- Détecte `.venv/` et `pyvenv.cfg`
- 🟢 "Found" si présent
- 🔴 "Not Found" + bouton "Fix Now" si absent

✅ **Price Database**
- Vérifie `models/cards_database.yaml`
- 🟢 "Found (YAML)" si présent
- 🟡 "Found (Excel legacy)" si ancien format
- 🔴 "Not Found" si manquant

✅ **YOLO Models**
- Liste des modèles détectés :
  - `yolo11n.pt` (YOLO11 nano)
  - `yolov8n.pt` (YOLOv8 nano)
- Téléchargement auto si manquants

### Auto-Refresh

Statistiques mises à jour automatiquement :
- **Intervalle** : 5 secondes
- **Thread séparé** : N'impacte pas l'UI
- **Désactivable** : Via Settings → Advanced

---

## 5. 🔄 Workflow Automatique

Le **Workflow Automatique** exécute un pipeline complet de 5 étapes en une seule action.

### Pipeline en 5 Étapes

```
1. 🎨 Augmentation
   ↓
2. 🧩 Génération Mosaïques
   ↓
3. ✅ Validation Dataset
   ↓
4. ⚖️ Auto-Balancing (optionnel)
   ↓
5. 🎓 Entraînement YOLO (optionnel)
```

### Configuration du Workflow

#### Étape 1 : Augmentation
- **Checkbox** : ✅ Activer/désactiver
- **Paramètres** :
  - Nombre d'augmentations : 5-100 (défaut: 15)
  - Inclure holographiques : Oui/Non
  - Dossier source : `images/`
  - Dossier sortie : `output/augmented/`

#### Étape 2 : Génération Mosaïques
- **Checkbox** : ✅ Activer/désactiver
- **Mode** :
  - 🚀 Quick (200 mosaïques)
  - ⚡ Standard (500 mosaïques)
  - 🔥 Complete (toutes combinaisons)
- **Dossier sortie** : `output/mosaics/`

#### Étape 3 : Validation
- **Checkbox** : ✅ Activer/désactiver
- **Vérifications** :
  - Annotations YOLO valides
  - Images non corrompues
  - Bounding boxes dans limites [0,1]
- **Rapport HTML** : `output/validation_report.html`

#### Étape 4 : Auto-Balancing
- **Checkbox** : ❌ Désactivé par défaut
- **Paramètres** :
  - Target count : 50 images/classe
  - Méthode : Random sampling
- **Sortie** : `output/balanced/`

#### Étape 5 : Entraînement YOLO
- **Checkbox** : ❌ Désactivé par défaut
- **Paramètres** :
  - Model : YOLOv8n ou YOLO11n
  - Epochs : 50 (défaut)
  - Batch size : 16 (défaut)
  - Image size : 640 (défaut)
- **Sortie** : `runs/detect/train/`

### Lancement du Workflow

1. **Configurer** les étapes (cocher/décocher)
2. **Ajuster** les paramètres si besoin
3. **Cliquer** "▶️ START WORKFLOW"
4. **Monitorer** la progression :
   - Barre de progression globale
   - Logs détaillés en temps réel
   - Temps écoulé
   - Étape en cours affichée
5. **Attendre** la fin (ou cliquer "⏹️ STOP" pour annuler)

### Durée Estimée

Calcul automatique affiché avant lancement :

| Configuration | Durée estimée |
|---------------|---------------|
| Augmentation seule (15×) | 2-5 minutes |
| + Mosaïques (500) | +5-10 minutes |
| + Validation | +1 minute |
| + Auto-Balancing | +2 minutes |
| + Training (50 epochs) | +30-60 minutes (CPU) ou +5-10 minutes (GPU) |

**Total workflow complet** : 40-80 minutes (CPU) / 15-30 minutes (GPU)

### Cas d'Usage

**Workflow pour débutants** :
```
✅ Augmentation (10×)
✅ Mosaïques (Quick 200)
✅ Validation
❌ Auto-Balancing (pas nécessaire au début)
❌ Training (faire manuellement après vérification)
```

**Workflow production** :
```
✅ Augmentation (20×)
✅ Mosaïques (Standard 500)
✅ Validation
✅ Auto-Balancing (50/classe)
✅ Training (100 epochs)
```

**Workflow test rapide** :
```
✅ Augmentation (5×)
✅ Mosaïques (Quick 200)
✅ Validation
❌ Auto-Balancing
❌ Training
```

---

## 6. ⬇️ Image Download

La vue **Image Download** permet de télécharger des cartes Pokémon depuis **TCGdex API** (gratuite, sans authentification).

### Pourquoi TCGdex ?

| Avantage | TCGdex | Pokemon TCG API | Cardmarket API |
|----------|---------|-----------------|----------------|
| **Authentification** | ❌ Aucune | ✅ Clé API | ✅ OAuth 1.0 |
| **Configuration** | 🟢 1 min | 🟡 5 min | 🔴 15+ min |
| **Vitesse** | ⚡ Ultra-rapide | 🐌 Moyen | 🐌 Lent |
| **Prix intégrés** | ✅ CM + TCP | ❌ Uniquement TCP | ✅ CM uniquement |
| **Multilingue** | ✅ 10+ langues | ❌ Anglais | ✅ Multilingue |
| **Coût** | 💰 GRATUIT | 💰 GRATUIT | 💰 GRATUIT |

**Conclusion** : TCGdex = Meilleur choix pour démarrer rapidement !

### Configuration de la Vue

#### 1. Pokémon Set (Requis)

**Option A : Sélection menu déroulant**
- Liste des 20+ sets les plus populaires
- Format affiché : "Surging Sparks (sv08)"
- ID automatiquement extrait

**Option B : Saisie manuelle**
- Entrer nom complet : "Surging Sparks"
- OU entrer ID direct : "sv08"
- Mapping automatique vers ID TCGdex

**Sets Populaires Disponibles** :

| Set Name | ID | Cartes | Année |
|----------|-----|--------|-------|
| Surging Sparks | sv08 | 191 | 2024 |
| Stellar Crown | sv07 | 175 | 2024 |
| Shrouded Fable | sv06.5 | 99 | 2024 |
| Twilight Masquerade | sv06 | 167 | 2024 |
| Temporal Forces | sv05 | 162 | 2024 |
| Paldean Fates | sv04.5 | 245 | 2024 |
| Paradox Rift | sv04 | 182 | 2023 |
| Obsidian Flames | sv03 | 197 | 2023 |
| Paldea Evolved | sv02 | 193 | 2023 |
| Scarlet & Violet | sv01 | 198 | 2023 |
| Base Set | base1 | 102 | 1999 |
| Jungle | base2 | 64 | 1999 |
| Fossil | base3 | 62 | 1999 |

#### 2. Language (Langue des cartes)

**10 langues supportées** :
- 🇬🇧 **en** - English (défaut)
- 🇫🇷 **fr** - Français
- 🇩🇪 **de** - Deutsch
- 🇮🇹 **it** - Italiano
- 🇪🇸 **es** - Español
- 🇵🇹 **pt** - Português
- 🇯🇵 **ja** - 日本語
- 🇰🇷 **ko** - 한국어
- 🇨🇳 **zh** - 中文
- 🇹🇭 **th** - ไทย

#### 3. Quality (Qualité d'image)

- **high** : Haute résolution (recommandé pour entraînement)
  - ~300-500 KB par image
  - Résolution : 734×1024 pixels typique
- **low** : Basse résolution (aperçu rapide)
  - ~50-100 KB par image
  - Résolution : 245×342 pixels typique

#### 4. Format (Format de fichier)

- **png** : Recommandé (sans perte, qualité maximale)
- **jpg** : Plus petit (compression avec perte)
- **webp** : Moderne (bon compromis taille/qualité)

#### 5. Output Directory

- **Défaut** : `images/`
- **Personnalisable** : Cliquez "Browse" pour choisir

**Structure créée** :
```
images/
└── sv08/                    # ID du set
    ├── sv08_001_en.png
    ├── sv08_002_en.png
    ├── ...
    ├── sv08_191_en.png
    └── manifest.csv         # Détails téléchargement
```

### Téléchargement

#### Lancement

1. **Configurer** tous les paramètres ci-dessus
2. **Cliquer** "⬇️ START DOWNLOAD"
3. **Monitorer** la progression :
   - Barre de progression : 0-100%
   - Logs : `Downloading card 23/191: Pikachu`
   - Temps restant estimé

#### Téléchargement Parallèle

- **Workers** : 4-8 threads simultanés (configurable dans Settings)
- **Vitesse** : 10-30 cartes/seconde (selon connexion)
- **Durée** : ~30-60 secondes pour 200 cartes

**Exemple** :
```
✅ Set: Surging Sparks (sv08)
✅ Language: English
✅ Quality: high
✅ Workers: 8

📊 Progress: 191/191 cards (100%)
⏱️ Duration: 45 seconds
💾 Total size: 95 MB
```

#### Gestion des Erreurs

**Retry automatique** :
- 3 tentatives par carte
- Délai exponentiel : 1s, 2s, 4s
- Skip si échec après 3 tentatives

**Logs d'erreurs** :
```
⚠️ Warning: Failed to download sv08_145_en.png (3 attempts)
ℹ️ Skipping card and continuing...
```

### Fichier Manifest

**manifest.csv généré** dans le dossier de sortie :

```csv
set_id,card_number,card_name,language,quality,format,filename,filesize,status
sv08,001,Exeggcute,en,high,png,sv08_001_en.png,342156,success
sv08,002,Exeggutor,en,high,png,sv08_002_en.png,389421,success
sv08,145,Pikachu ex,en,high,png,sv08_145_en.png,failed,error
...
```

**Utilité** :
- Traçabilité des téléchargements
- Identification des échecs
- Statistiques (taille totale, durée, etc.)

### Bouton "📂 Open Folder"

Cliquer pour ouvrir directement `images/{set_id}/` dans l'explorateur Windows.

---

## 7. 🎨 Augmentation

La vue **Augmentation** génère des **variations** de vos cartes originales en appliquant **22+ techniques de transformation**.

### Objectif

**Pourquoi augmenter ?**
- ✅ **Augmenter la quantité** : 10 images → 100+ images
- ✅ **Améliorer la robustesse** : Modèle généralisable
- ✅ **Simuler conditions réelles** : Éclairage, flou, rotation, etc.
- ✅ **Éviter overfitting** : Variété empêche mémorisation

### Configuration

#### Nombre d'Augmentations
- **Range** : 1-100 variations par image
- **Défaut** : 15
- **Recommandation** :
  - Début : 10-15 variations
  - Production : 20-30 variations
  - Maximum : 50-100 (si peu d'images sources)

#### Source Directory
- **Défaut** : `images/`
- **Changeable** : Cliquez "Browse"
- **Formats acceptés** : `.png`, `.jpg`, `.jpeg`, `.webp`

#### Output Directory
- **Défaut** : `output/augmented/`
- **Structure créée** :
  ```
  output/augmented/
  ├── images/               # Images augmentées
  │   ├── sv08_001_en_aug_001.png
  │   ├── sv08_001_en_aug_002.png
  │   └── ...
  ├── labels/               # Annotations YOLO
  │   ├── sv08_001_en_aug_001.txt
  │   ├── sv08_001_en_aug_002.txt
  │   └── ...
  └── data.yaml             # Configuration YOLO
  ```

#### Include Holographic
- **Checkbox** : ✅ Activer pour ajouter effets holographiques
- **Effet** : Chaque variation peut avoir en plus un effet shiny
- **Résultat** : Double le nombre d'images finales

### Techniques d'Augmentation (25 types)

Pipeline **Albumentations** avec sélection aléatoire : **3 à 6 transformations** appliquées par image.

#### 🌞 Luminosité & Contraste
1. **Add (-20, +20)** : Ajuste luminosité (±20 pixels)
2. **Multiply (0.8, 1.2)** : Multiplie contraste (80-120%)

#### 🔄 Transformations Géométriques
3. **Rotate (-15°, +15°)** : Rotation légère
4. **ShearX (-10°, +10°)** : Cisaillement horizontal
5. **ShearY (-10°, +10°)** : Cisaillement vertical
6. **Flip LR** : Miroir horizontal (50% de chance)
7. **Flip UD** : Miroir vertical (10% de chance)

#### 🎨 Effets de Couleur
8. **Hue Shift (-20, +20)** : Change la teinte
9. **Saturation (0.7, 1.3)** : Ajuste la saturation
10. **Grayscale (0.0, 0.3)** : Désaturation partielle

#### 🌫️ Flou & Netteté
11. **Gaussian Blur (0.0, 1.5)** : Flou gaussien léger
12. **Average Blur (1, 3)** : Flou moyen
13. **Median Blur (1, 3)** : Flou médian (réduit bruit)
14. **Sharpen (0.0, 0.5)** : Accentuation netteté

#### 🔍 Déformations
15. **Affine Scale (0.9, 1.1)** : Zoom in/out léger
16. **Perspective (0.05)** : Transformation perspective
17. **Elastic Transform** : Déformation élastique légère
18. **Piecewise Affine (0.01, 0.03)** : Déformation par zones

#### 🌈 Effets Avancés
19. **Gaussian Noise** : Bruit gaussien léger
20. **Dropout (0.0, 0.03)** : Dropout de pixels (3% max)
21. **CoarseDropout** : Dropout par blocs
22. **LinearContrast (0.8, 1.2)** : Contraste linéaire

### Lancement

1. **Configurer** :
   - Nombre d'augmentations : 15
   - Source : `images/`
   - Output : `output/augmented/`
   - ✅ Include Holographic
2. **Cliquer** "▶️ START AUGMENTATION"
3. **Progression** :
   ```
   🎨 Processing: sv08_001_en.png (1/191)
   ✅ Generated 15 augmentations
   🎨 Processing: sv08_002_en.png (2/191)
   ...
   ✅ Total: 2865 images generated (191 × 15)
   ⏱️ Duration: 3m 45s
   ```

### Statistiques en Temps Réel

**Compteur mis à jour toutes les 2 secondes** :
- 📂 Source Images : 191
- ✨ Holographic Images : 0 (ou nombre si activé)
- 🎨 Augmented Images : 2865 (en progression)

### Bouton "📂 Open Folder"

Ouvre `output/augmented/images/` dans l'explorateur.

### Optimisations Performance (v3.2.2)

- **Parallélisation** : Multi-threading automatique
- **Batch processing** : Traitement par lots
- **RAM caching** : Images chargées en cache
- **Durée** : ~0.5-1 seconde par image × nombre d'augmentations

**Exemple** :
```
191 images × 15 augmentations = 2865 images
Durée : ~5-10 minutes (CPU)
```

---

## 8. ✨ Effets Holographiques

La vue **Holographic** ajoute des **effets brillants et irisés** sur vos cartes pour simuler les vraies cartes holographiques Pokémon.

### Objectif

**Pourquoi ajouter des effets holographiques ?**
- ✅ **Simuler cartes réelles** : Beaucoup de cartes Pokémon ont des finitions holographiques
- ✅ **Améliorer généralisation** : Modèle reconnaît cartes avec ou sans effet brillant
- ✅ **Augmenter variété** : Diversité visuelle pour robustesse
- ✅ **Conditions d'éclairage** : Simule reflets lumineux réalistes

### Configuration

#### Intensity (Intensité)
- **Range** : 0.1-1.0 (slider)
- **Défaut** : 0.7
- **Effet** :
  - 0.1-0.3 : Effet subtil (léger reflet)
  - 0.4-0.7 : Effet modéré (recommandé)
  - 0.8-1.0 : Effet intense (très brillant)

#### Variations
- **Range** : 1-10
- **Défaut** : 3
- **Effet** : Nombre de variations d'angle par carte

#### Source Directory
- **Défaut** : `images/` ou `output/augmented/images/`
- **Formats acceptés** : `.png`, `.jpg`, `.jpeg`, `.webp`

#### Output Directory
- **Défaut** : `output/holographic/`
- **Structure créée** :
  ```
  output/holographic/
  ├── sv08_001_en_holo_1.png
  ├── sv08_001_en_holo_2.png
  ├── sv08_001_en_holo_3.png
  └── ...
  ```

### 5+ Styles d'Effets Holographiques

#### 1. 🌈 Rainbow Gradient
- **Description** : Dégradé arc-en-ciel qui balaie la carte
- **Effet** : Simule reflet holographique classique
- **Angle** : Varie selon la variation (0°, 45°, 90°, etc.)
- **Optimisation v3.2.2** : **50-100x plus rapide** (vectorisation NumPy)

#### 2. ✨ Dynamic Glare
- **Description** : Points lumineux brillants mobiles
- **Effet** : Simule éclairage direct sur surface holographique
- **Position** : Varie selon variation
- **Optimisation v3.2.2** : **10-20x plus rapide**

#### 3. 💎 Metallic Shine
- **Description** : Reflet métallique avec contraste élevé
- **Effet** : Simule finition métallique (Ultra Rare, Full Art)
- **Intensité** : Contrôlée par le slider

#### 4. ⚡ Glitter Sparkle
- **Description** : Petits points scintillants éparpillés
- **Effet** : Simule particules holographiques (Holo Rare)
- **Densité** : 1000-5000 particules selon intensité

#### 5. 🎨 Color Shift
- **Description** : Changement de teinte selon angle de vue
- **Effet** : Simule encre chromée (Secret Rare)
- **Couleurs** : Rouge→Vert→Bleu→Violet

### Pipeline de Génération

**Pour chaque image source** :
1. **Charger** l'image originale
2. **Générer N variations** (défaut: 3)
3. **Appliquer effet holographique** :
   - Choisir style aléatoire
   - Calculer paramètres (angle, position, intensité)
   - Appliquer transformation
4. **Sauvegarder** avec suffix `_holo_N`

### Lancement

1. **Configurer** :
   - Intensity : 0.7
   - Variations : 3
   - Source : `output/augmented/images/`
   - Output : `output/holographic/`
2. **Cliquer** "▶️ START HOLOGRAPHIC"
3. **Progression** :
   ```
   ✨ Processing: sv08_001_en.png (1/191)
   ✅ Generated 3 holographic variations
   ✨ Processing: sv08_002_en.png (2/191)
   ...
   ✅ Total: 573 holographic images (191 × 3)
   ⏱️ Duration: 1m 20s (avec optimisations v3.2.2)
   ```

### Optimisations Performance (v3.2.2)

**Avant optimisation** :
- 252 cartes × 3 variations = **11-20 minutes** (CPU)
- Boucles imbriquées pixel par pixel

**Après optimisation v3.2.2** :
- 252 cartes × 3 variations = **4-10 secondes** (CPU)
- **100-300x plus rapide** grâce à :
  - ✅ Vectorisation NumPy (meshgrid, broadcasting)
  - ✅ Distance calculations vectorisées
  - ✅ Pattern generation optimisée
  - ✅ Élimination boucles imbriquées

**Détails techniques** :
```python
# Avant (lent) :
for y in range(height):
    for x in range(width):
        gradient[y, x] = calculate_color(x, y)

# Après (rapide) :
X, Y = np.meshgrid(np.arange(width), np.arange(height))
gradient = calculate_color_vectorized(X, Y)
```

### Intégration avec Augmentation

**Option "Both"** dans vue Augmentation :
- Génère augmentations classiques
- Puis applique effets holographiques sur chaque augmentation
- **Résultat** : Double le nombre d'images finales

**Exemple** :
```
10 images sources × 15 augmentations = 150 images
+ 150 images holographiques = 300 images total
```

### Bouton "📂 Open Folder"

Ouvre `output/holographic/` dans l'explorateur Windows.

---

## 9. 🧩 Génération de Mosaïques

La vue **Mosaic Generator** crée des **scènes composites** avec plusieurs cartes sur des fonds variés, idéales pour l'entraînement YOLO.

### Objectif

**Pourquoi générer des mosaïques ?**
- ✅ **Scènes réalistes** : Multiple cartes ensemble (comme photos réelles)
- ✅ **Détection multi-objets** : Entraîne YOLO à détecter plusieurs cartes simultanément
- ✅ **Variété de layouts** : Positions, rotations, échelles différentes
- ✅ **Contexte riche** : Backgrounds variés, occlusions partielles
- ✅ **Annotations automatiques** : Bounding boxes et polygones 4 points générés auto

### 3 Modes de Génération

#### 🚀 Mode Quick (200 mosaïques)
- **Groupes** : 25 groupes de 8 cartes
- **Durée** : ~2-3 minutes
- **Usage** : Tests rapides, prototypage
- **Variété** : Basse (1 layout, 1 background, 1 transform)

#### ⚡ Mode Standard (500 mosaïques - RECOMMANDÉ)
- **Groupes** : 62 groupes de 8 cartes
- **Durée** : ~5-10 minutes
- **Usage** : Production, entraînement normal
- **Variété** : Moyenne (2 layouts, 2 backgrounds, 1 transform)

#### 🔥 Mode Complete (800-1000 mosaïques)
- **Groupes** : Tous (dépend du nombre de cartes)
- **Durée** : ~15-30 minutes
- **Usage** : Dataset maximal, compétition
- **Variété** : Maximale (3 layouts × 3 backgrounds × 2 transforms)

### Paramètres Détaillés

#### Layout Mode (Disposition des cartes)

**Layout 1 : Grille régulière avec rotation légère**
- Disposition : Grille 4×2 (4 colonnes, 2 rangées)
- Rotation : ±10-20° aléatoire
- Espacement : Uniforme et prévisible
- **Usage** : Cartes bien séparées, facile à détecter

**Layout 2 : Grille avec rotation forte**
- Disposition : Grille 4×2
- Rotation : Jusqu'à ±180° (toutes orientations)
- Flip : Possibles (horizontal/vertical)
- **Usage** : Simule cartes désordonnées

**Layout 3 : Position complètement aléatoire**
- Disposition : Positions X,Y aléatoires
- Rotation : 0-360° aléatoire
- Échelle : 0.3-0.8× aléatoire
- Overlapping : Possible (cartes se chevauchent)
- **Usage** : Maximum de variété, scènes chaotiques

#### Background Mode (Type de fond)

**Background 0 : Mosaïque de fausses cartes**
- Source : `output/backgrounds/` (fake images)
- Création : Grille de fausses cartes générées
- **Avantage** : Contexte "cartes sur table"
- **Performance** : Rapide (pré-générées)

**Background 1 : Images locales**
- Source : Dossier personnalisé (si fourni)
- Formats : JPG, PNG, WEBP
- **Avantage** : Backgrounds custom
- **Exemple** : Photos de table, tapis, surface bois

**Background 2 : Images du web**
- Source : Lorem Picsum (placeholder service)
- Résolution : 1920×1080 pixels
- **Avantage** : Variété infinie
- **Note** : Nécessite connexion Internet

#### Transform Mode (Type de transformation)

**Transform 0 : Rotation 2D classique**
- Transformation : `cv2.warpAffine()`
- Paramètres : Angle de rotation seulement
- **Effet** : Cartes plates, rotation simple
- **Performance** : Rapide

**Transform 1 : Projection perspective 3D**
- Transformation : `cv2.warpPerspective()`
- Paramètres : Angles theta (inclinaison) et phi (orientation)
- **Effet** : Cartes inclinées, vue 3D réaliste
- **Performance** : Légèrement plus lent

### Configuration de la Vue

#### Mode Selection
- **Dropdown** : Quick / Standard / Complete
- **Sélection** : Change automatiquement les paramètres

#### Custom Parameters (Advanced)
- **Max Groups** : Limiter nombre de groupes (1-∞)
- **Layout Mode** : 1, 2, ou 3
- **Background Mode** : 0, 1, ou 2
- **Transform Mode** : 0 ou 1

#### Output Directory
- **Défaut** : `output/mosaics/`
- **Structure créée** :
  ```
  output/mosaics/
  ├── images/
  │   ├── L1_B0_T0_mosaic_g001_c001.jpg
  │   ├── L1_B0_T0_mosaic_g001_c002.jpg
  │   └── ...
  ├── labels/
  │   ├── L1_B0_T0_mosaic_g001_c001.txt
  │   ├── L1_B0_T0_mosaic_g001_c002.txt
  │   └── ...
  ├── data.yaml
  └── annotations.json
  ```

**Format de nommage** (v3.2.1+) :
- `L{layout}_B{background}_T{transform}_mosaic_g{group}_c{combination}.jpg`
- Exemple : `L1_B0_T0_mosaic_g001_c001.jpg`
  - Layout 1, Background 0, Transform 0
  - Groupe 1, Combinaison 1

### Annotations Automatiques

#### Format YOLO (.txt files)
Chaque fichier label contient **1 ligne par carte** :
```
<class_id> <x1> <y1> <x2> <y2> <x3> <y3> <x4> <y4>
```

**8 valeurs** : Polygone 4 points (coins de la carte)
- Coordonnées normalisées [0, 1]
- Ordre : top-left, top-right, bottom-right, bottom-left

**Exemple** :
```
0 0.1 0.2 0.3 0.2 0.3 0.6 0.1 0.6
1 0.5 0.3 0.7 0.3 0.7 0.7 0.5 0.7
2 0.2 0.5 0.4 0.5 0.4 0.9 0.2 0.9
```

#### Fichier annotations.json
Métadonnées détaillées pour chaque mosaïque :
```json
{
  "L1_B0_T0_mosaic_g001_c001.jpg": {
    "cards": [
      {
        "class_id": 0,
        "card_name": "Pikachu",
        "card_number": "025",
        "polygon": [[0.1, 0.2], [0.3, 0.2], [0.3, 0.6], [0.1, 0.6]],
        "rotation": 15.3,
        "scale": 0.85
      },
      // ... 7 autres cartes
    ],
    "layout": 1,
    "background": 0,
    "transform": 0
  }
}
```

### Lancement

1. **Sélectionner mode** : Quick / Standard / Complete
2. (**Optionnel**) Configurer paramètres avancés
3. **Cliquer** "▶️ GENERATE MOSAICS"
4. **Progression** :
   ```
   🧩 Layout: 1, Background: 0, Transform: 0
   🎯 Generating group 1/62 (25 cards)
   ✅ Generated 8 mosaics for group 1
   🎯 Generating group 2/62 (25 cards)
   ...
   ✅ Total: 496 mosaics generated
   ⏱️ Duration: 7m 30s
   ```

### Optimisations Performance (v3.2.1)

**Avant optimisation** :
- 8000 images → 1000 mosaics = **45-90 minutes** (séquentiel)
- CRC errors fréquents
- Mode Complete crashait

**Après optimisation v3.2.1** :
- 8000 images → 1000 mosaics = **1.5-3 minutes** (parallèle)
- **30-60x plus rapide** grâce à :
  - ✅ `ProcessPoolExecutor` : Vrai parallélisme (bypass GIL Python)
  - ✅ Auto-detection CPU cores (utilise tous les cœurs)
  - ✅ PNG compression = 0 : Écriture ultra-rapide
  - ✅ Gestion erreurs robuste : Continue si image corrompue
  - ✅ Prefix system : Pas d'écrasement entre runs

**Détails techniques** :
```python
# ProcessPoolExecutor (vrai parallélisme) :
with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
    futures = [executor.submit(generate_mosaic, group) for group in groups]
    
# PNG sans compression (30-50% plus rapide) :
cv2.imwrite(filename, image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
```

### Gestion des Images Corrompues

**Nouveau v3.2.1** : Auto-recovery
- Détecte images CRC error ou corrompues
- Déplace automatiquement vers `corrupted/`
- Continue génération sans interruption
- Logs détaillés des fichiers problématiques

**Exemple** :
```
⚠️ Warning: Corrupted image detected: sv08_145_en_aug_012.png
📁 Moved to: corrupted/sv08_145_en_aug_012.png
ℹ️ Continuing with next image...
```

### Bouton "📂 Open Folder"

Ouvre `output/mosaics/images/` dans l'explorateur Windows.

---

## 10. 🖼️ Fake Images (Backgrounds)

La vue **Fake Images** génère des **backgrounds synthétiques** avec Random Erasing pour créer des fonds variés pour les mosaïques.

### Objectif

**Pourquoi générer des fake backgrounds ?**
- ✅ **Fonds variés** : Évite répétition des mêmes backgrounds
- ✅ **Textures réalistes** : Bruit Perlin simule surfaces naturelles
- ✅ **Performance** : Pré-générer évite téléchargements web
- ✅ **Contrôle** : Maîtrise complète sur l'apparence

### Configuration

#### Count (Nombre d'images)
- **Range** : 10-1000
- **Défaut** : 100
- **Recommandation** :
  - Tests : 50-100
  - Production : 200-500
  - Maximum variété : 1000+

#### Noise Min (Bruit minimum)
- **Range** : 0-100
- **Défaut** : 10
- **Effet** : Intensité minimale du bruit Perlin
  - 0-20 : Surface lisse
  - 20-40 : Texture modérée
  - 40-100 : Texture forte

#### Noise Max (Bruit maximum)
- **Range** : 0-100
- **Défaut** : 50
- **Effet** : Intensité maximale du bruit Perlin
  - Variation aléatoire entre Min et Max
  - Plus grande plage = plus de variété

#### Output Directory
- **Défaut** : `output/backgrounds/`
- **Remplace** : Ancien `backgrounds/augmented/` (v3.2.3+)
- **Structure créée** :
  ```
  output/backgrounds/
  ├── fake_bg_001.png
  ├── fake_bg_002.png
  ├── fake_bg_003.png
  └── ...
  ```

### Techniques de Génération

#### 1. Bruit Perlin
- **Algorithme** : Noise cohérent avec gradients
- **Effet** : Texture organique, non répétitive
- **Échelles** : Multi-octaves pour détails (4-8 octaves)

#### 2. Random Erasing
- **Algorithme** : Blocs rectangulaires aléatoires
- **Couleurs** : RGB aléatoires ou dégradés
- **Tailles** : 10-50% de l'image
- **Nombre** : 5-20 blocs par image

#### 3. Color Variations
- **Teinte** : Shift HSV aléatoire
- **Saturation** : 0.5-1.5×
- **Luminosité** : 0.7-1.3×

#### 4. Gradient Overlays
- **Types** : Linéaire, radial, diagonal
- **Opacité** : 10-30%
- **Effet** : Variation d'éclairage réaliste

### Lancement

1. **Configurer** :
   - Count : 200
   - Noise Min : 10
   - Noise Max : 50
   - Output : `output/backgrounds/`
2. **Cliquer** "▶️ START GENERATION"
3. **Progression** :
   ```
   🖼️ Generating fake background 1/200
   ✅ Saved: fake_bg_001.png
   🖼️ Generating fake background 2/200
   ...
   ✅ Total: 200 backgrounds generated
   ⏱️ Duration: 45 seconds
   💾 Total size: 87 MB
   ```

### Utilisation dans Mosaïques

**Automatique** :
- Lorsque Background Mode = 0 (Mosaic)
- Pioche aléatoirement dans `output/backgrounds/`
- Crée grille 4×2 de fakes en arrière-plan
- Place les vraies cartes par-dessus

### Settings Configuration

**Settings → Fake Backgrounds Tab** :
- Default Count
- Default Noise Min
- Default Noise Max
- Output Directory
- Image Size (1920×1080 défaut)

### Bouton "📂 Open Folder"

Ouvre `output/backgrounds/` dans l'explorateur Windows.

---

## 11. ✅ Validation Dataset

La vue **Validation** vérifie l'**intégrité et qualité** de votre dataset YOLO avant l'entraînement.

### Objectif

**Pourquoi valider ?**
- ✅ **Éviter erreurs entraînement** : Détecte problèmes AVANT de lancer training
- ✅ **Qualité garantie** : Assure annotations correctes
- ✅ **Statistiques claires** : Distribution des classes visible
- ✅ **Rapport HTML** : Documentation complète des vérifications

### Vérifications Effectuées

#### 1. ✅ Format YOLO Valide
- **Check** : Structure des fichiers `.txt`
- **Validation** :
  - Nombre de valeurs correct (5 pour bbox, 8 pour polygon)
  - Valeurs numériques valides
  - Pas de lignes vides ou corrompues
- **Erreur typique** : `Invalid YOLO format in file.txt line 3`

#### 2. ✅ Images Non Corrompues
- **Check** : Intégrité des fichiers images
- **Validation** :
  - Fichier lisible par OpenCV
  - Header valide (PNG, JPG, WEBP)
  - Dimensions > 0
  - Pas de CRC error
- **Erreur typique** : `Corrupted image: file.png (CRC error)`

#### 3. ✅ Matching Images ↔ Labels
- **Check** : Chaque image a un label correspondant
- **Validation** :
  - `image.png` → `image.txt` existe
  - Pas d'orphelins (image sans label ou inverse)
- **Erreur typique** : `Missing label for image: file.png`

#### 4. ✅ Bounding Boxes Valides
- **Check** : Coordonnées dans limites [0, 1]
- **Validation** :
  - x_center, y_center ∈ [0, 1]
  - width, height ∈ [0, 1]
  - Pas de valeurs négatives
  - Pas de bbox hors image
- **Erreur typique** : `Invalid bbox in file.txt: x=1.2 (out of range)`

#### 5. ✅ Distribution des Classes
- **Check** : Nombre d'images par classe
- **Calcul** :
  - Compte toutes les annotations
  - Groupe par class_id
  - Calcule min/max/moyenne
- **Warning** : Si déséquilibre > 5:1 ratio

### Configuration

#### Dataset Directory
- **Défaut** : `output/mosaics/` (ou `output/augmented/`)
- **Formats** : YOLO standard (images/ + labels/ + data.yaml)
- **Changeable** : Bouton "Browse"

#### Validation Options
- **Check Images** : ✅ Activé (vérifier intégrité)
- **Check Labels** : ✅ Activé (vérifier format YOLO)
- **Check Distribution** : ✅ Activé (statistiques classes)
- **Generate HTML Report** : ✅ Activé (rapport détaillé)

### Lancement

1. **Sélectionner dataset** : `output/mosaics/`
2. **Cliquer** "▶️ START VALIDATION"
3. **Progression** :
   ```
   ✅ Checking images: 496/496 (100%)
   ✅ Valid images: 496
   ❌ Corrupted: 0
   
   ✅ Checking labels: 496/496 (100%)
   ✅ Valid labels: 496
   ❌ Invalid: 0
   
   ✅ Matching check:
   ✅ All images have labels
   ✅ All labels have images
   
   📊 Class distribution:
   Class 0 (Pikachu): 1984 annotations
   Class 1 (Charizard): 1856 annotations
   Class 2 (Mewtwo): 2048 annotations
   ...
   
   ✅ Validation complete!
   📄 HTML report: output/mosaics/validation_report.html
   ```

### Rapport HTML

**Contenu du rapport** :

#### Section 1 : Summary
- Total images : 496
- Total labels : 496
- Valid images : 496 (100%)
- Valid labels : 496 (100%)
- Matching : 100%

#### Section 2 : Class Distribution
- **Tableau** : Class ID | Name | Count | Percentage
- **Graphique** : Bar chart de la distribution
- **Statistiques** :
  - Min : 125 images (Class 15)
  - Max : 385 images (Class 3)
  - Mean : 248 images
  - Std Dev : 87

#### Section 3 : Errors & Warnings
- **Liste détaillée** :
  - Fichier concerné
  - Type d'erreur
  - Ligne (si applicable)
  - Message descriptif
- **Exemple** :
  ```
  ⚠️ Warning: Class imbalance detected
  Class 3 has 385 images (3× more than Class 15: 125 images)
  Recommendation: Use Auto-Balancer to equalize distribution
  ```

#### Section 4 : Recommendations
- Suggestions automatiques selon erreurs détectées
- Actions correctives proposées
- Liens vers documentation

### Auto-ouverture du Rapport

**Par défaut** : Le rapport HTML s'ouvre automatiquement dans votre navigateur après validation.

**Désactiver** : Settings → Validation → ❌ Auto-open Report

### Actions Correctives

**Si erreurs détectées** :

1. **Images corrompues** →
   - Ré-augmenter les images sources
   - OU supprimer images + labels correspondants

2. **Labels invalides** →
   - Vérifier script d'annotation
   - Ré-générer mosaïques avec corrections

3. **Matching problems** →
   - Supprimer orphelins
   - Vérifier noms de fichiers cohérents

4. **Class imbalance** →
   - Utiliser Auto-Balancer (vue suivante)
   - OU générer plus d'augmentations pour classes sous-représentées

### Bouton "📂 Open Report"

Ouvre `validation_report.html` dans le navigateur par défaut.

---

## 12. ⚖️ Auto-Balancing

La vue **Auto-Balance** équilibre automatiquement la **distribution des classes** dans votre dataset.

### Objectif

**Pourquoi équilibrer les classes ?**
- ✅ **Éviter biais** : Modèle ne favorise pas classes sur-représentées
- ✅ **Performances uniformes** : mAP égal sur toutes les classes
- ✅ **Entraînement stable** : Convergence plus rapide
- ✅ **Généralisation** : Meilleure détection des classes rares

### Problème du Déséquilibre

**Exemple de déséquilibre** :
```
Class 0 (Pikachu): 500 images  ← Sur-représenté
Class 1 (Mewtwo): 450 images
Class 2 (Charizard): 480 images
Class 3 (Bulbasaur): 50 images  ← Sous-représenté
Class 4 (Squirtle): 75 images   ← Sous-représenté
```

**Conséquences** :
- ❌ Modèle détecte bien Pikachu (500 exemples)
- ❌ Modèle détecte mal Bulbasaur (50 exemples seulement)
- ❌ Biais vers classes fréquentes
- ❌ Perte de précision globale

### Stratégie d'Équilibrage

#### Méthode : Random Sampling

**Sur-échantillonnage (Upsampling)** :
- Classes sous-représentées → Dupliquer images aléatoirement
- Exemple : Bulbasaur (50) → 200 images (4× duplication)

**Sous-échantillonnage (Downsampling)** :
- Classes sur-représentées → Réduire aléatoirement
- Exemple : Pikachu (500) → 200 images (sélection random)

**Résultat équilibré** :
```
Class 0 (Pikachu): 200 images
Class 1 (Mewtwo): 200 images
Class 2 (Charizard): 200 images
Class 3 (Bulbasaur): 200 images
Class 4 (Squirtle): 200 images
```

### Configuration

#### Target Count (Images par classe)
- **Range** : 10-1000
- **Défaut** : 50
- **Recommandation** :
  - Petits datasets : 30-50 images/classe
  - Datasets moyens : 100-200 images/classe
  - Grands datasets : 300-500 images/classe
  - **Note** : Plus = mieux, mais durée entraînement ↑

#### Source Directory
- **Défaut** : `output/mosaics/`
- **Formats** : YOLO standard (images/ + labels/)

#### Output Directory
- **Défaut** : `output/balanced/`
- **Structure créée** :
  ```
  output/balanced/
  ├── images/
  │   ├── class_0_001.jpg
  │   ├── class_0_002.jpg (peut être duplicate)
  │   ├── class_1_001.jpg
  │   └── ...
  ├── labels/
  │   ├── class_0_001.txt
  │   ├── class_0_002.txt
  │   ├── class_1_001.txt
  │   └── ...
  └── data.yaml
  ```

#### Balancing Method
- **Random** : Sélection aléatoire (défaut)
- **Sequential** : Dans l'ordre d'apparition
- **Stratified** : Préserve distribution intra-classe

### Lancement

1. **Configurer** :
   - Target Count : 200
   - Source : `output/mosaics/`
   - Output : `output/balanced/`
   - Method : Random
2. **Cliquer** "▶️ START BALANCING"
3. **Progression** :
   ```
   📊 Original distribution:
   Class 0: 500 images
   Class 1: 450 images
   Class 2: 480 images
   Class 3: 50 images
   Class 4: 75 images
   
   ⚖️ Balancing to 200 images per class...
   
   ↓ Downsampling Class 0: 500 → 200 (random selection)
   ↓ Downsampling Class 1: 450 → 200 (random selection)
   ↓ Downsampling Class 2: 480 → 200 (random selection)
   ↑ Upsampling Class 3: 50 → 200 (4× duplication)
   ↑ Upsampling Class 4: 75 → 200 (2.67× duplication)
   
   ✅ Balanced distribution:
   Class 0: 200 images
   Class 1: 200 images
   Class 2: 200 images
   Class 3: 200 images
   Class 4: 200 images
   
   💾 Total: 1000 images (was 1555)
   📁 Saved to: output/balanced/
   ⏱️ Duration: 12 seconds
   ```

### data.yaml Mis à Jour

**Fichier généré** : `output/balanced/data.yaml`

```yaml
train: output/balanced/images
val: output/balanced/images  # Split train/val à faire manuellement

nc: 5  # Nombre de classes
names: ['Pikachu', 'Mewtwo', 'Charizard', 'Bulbasaur', 'Squirtle']

# Balancing info
balanced: true
target_count: 200
original_counts: [500, 450, 480, 50, 75]
balanced_counts: [200, 200, 200, 200, 200]
```

### Quand Utiliser l'Auto-Balancing ?

**✅ OUI** :
- Déséquilibre > 2:1 ratio (ex: 500 vs 250)
- Classes rares < 50 images
- Performance inégale entre classes
- Avant entraînement de production

**❌ NON** :
- Dataset déjà équilibré (±20% variation OK)
- Peu de données (< 10 images/classe)
- Distribution reflète réalité voulue

### Limitations

⚠️ **Sur-échantillonnage excessif** :
- Dupliquer 10 images en 200 = **overfitting** probable
- Solution : Générer plus d'augmentations au lieu de dupliquer

⚠️ **Perte d'information** :
- Sous-échantillonner 500 → 50 = **perte de 90%** des données
- Solution : Augmenter target_count si possible

### Bouton "📂 Open Folder"

Ouvre `output/balanced/` dans l'explorateur Windows

---

## 13. 🎓 Entraînement YOLO

La vue **Training** permet d'entraîner un modèle **YOLOv8 ou YOLO11** directement depuis l'interface GUI.

### Objectif

**Pourquoi entraîner YOLO ?**
- ✅ **Détection personnalisée** : Modèle spécifique à vos cartes Pokémon
- ✅ **Performance optimale** : Fine-tuned sur votre dataset
- ✅ **Multi-classes** : Détecte simultanément toutes vos cartes
- ✅ **Transfer learning** : Part d'un modèle pré-entraîné (COCO)

### Configuration

#### Model Selection (Choix du modèle)

| Model | Paramètres | Vitesse | Précision | VRAM | Usage |
|-------|------------|---------|-----------|------|-------|
| **YOLOv8n** | 3.2M | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | 2 GB | Production rapide |
| **YOLOv8s** | 11.2M | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 4 GB | Équilibre |
| **YOLOv8m** | 25.9M | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 6 GB | Précision élevée |
| **YOLOv8l** | 43.7M | ⚡⚡ | ⭐⭐⭐⭐⭐ | 8 GB | Maximum précision |
| **YOLOv8x** | 68.2M | ⚡ | ⭐⭐⭐⭐⭐ | 12 GB | Compétition |
| **YOLO11n** | 2.6M | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 2 GB | Dernière version (2024) |
| **YOLO11s** | 9.4M | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 4 GB | YOLO11 équilibré |

**Recommandation** :
- **Débuts** : YOLOv8n ou YOLO11n (rapide, léger)
- **Production** : YOLOv8s ou YOLO11s (bon compromis)
- **Compétition** : YOLOv8m ou supérieur

#### Dataset Path
- **Défaut** : `output/balanced/` (si balancé) ou `output/mosaics/`
- **Requis** : Structure YOLO standard (images/ + labels/ + data.yaml)
- **Changeable** : Bouton "Browse"

#### Epochs (Époques d'entraînement)
- **Range** : 1-1000
- **Défaut** : 50
- **Recommandation** :
  - Tests rapides : 10-20 epochs
  - Entraînement normal : 50-100 epochs
  - Fine-tuning : 100-300 epochs
  - **Note** : Plus n'est pas toujours mieux (risque d'overfitting)

#### Batch Size (Taille de lot)
- **Range** : 1-64 (selon VRAM disponible)
- **Défaut** : 16
- **Recommandation selon GPU** :
  - 2 GB VRAM → batch 4-8
  - 4 GB VRAM → batch 8-16
  - 6 GB VRAM → batch 16-32
  - 8+ GB VRAM → batch 32-64
- **Note** : Plus grand batch = entraînement plus rapide mais plus de VRAM

#### Image Size (Résolution)
- **Options** : 320, 416, 512, 640, 800, 1024, 1280
- **Défaut** : 640
- **Recommandation** :
  - Petites cartes / Rapide → 416-512
  - Standard (recommandé) → 640
  - Haute précision → 800-1024
  - **Note** : Plus grand = meilleure précision mais plus lent

#### Device (Matériel)
- **Auto** : Détection automatique (recommandé)
- **CPU** : Force utilisation CPU (lent mais compatible)
- **CUDA:0** : GPU 0 (si disponible)
- **CUDA:1** : GPU 1 (si multi-GPU)
- **MPS** : Apple Silicon (Mac M1/M2/M3)

**Détection automatique** :
```python
# Auto-détection
if torch.cuda.is_available():
    device = "cuda:0"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"
```

#### Workers (Processeurs de données)
- **Range** : 1-32
- **Défaut** : 8 (auto-détecté selon CPU cores)
- **Recommandation** : CPU cores - 2 (laisse ressources pour l'OS)

#### Pretrained
- **Checkbox** : ✅ Utiliser poids pré-entraînés (COCO dataset)
- **Défaut** : Activé (RECOMMANDÉ)
- **Avantage** : Transfer learning = convergence plus rapide
- **Désactiver** : Seulement si entraînement from scratch voulu

#### Cache
- **Checkbox** : ✅ Cacher images en RAM
- **Défaut** : Activé
- **Avantage** : Entraînement 2-3× plus rapide
- **Désactiver** : Si RAM limitée (< 8 GB)

#### Resume
- **Checkbox** : ❌ Reprendre entraînement interrompu
- **Défaut** : Désactivé
- **Usage** : Cocher si entraînement précédent interrompu
- **Requis** : Fichier `last.pt` dans `runs/detect/train/weights/`

### Lancement de l'Entraînement

1. **Configurer** tous les paramètres ci-dessus
2. **Cliquer** "▶️ START TRAINING"
3. **Monitorer** la progression :
   - Barre de progression : 0-100% (par epoch)
   - Logs en temps réel :
     ```
     Epoch 1/50 ━━━━━━━━━━━━━━━━━━━━━━ 100% 0:02:15
       train/box_loss: 0.02154
       train/cls_loss: 0.01847
       train/dfl_loss: 0.01234
       val/mAP50: 0.856
       val/mAP50-95: 0.643
     
     Epoch 2/50 ━━━━━━━━━━━━━━━━━━━━━━ 100% 0:02:10
       train/box_loss: 0.01987
       ...
     ```

4. **Métriques affichées** :
   - **box_loss** : Erreur localisation bounding box
   - **cls_loss** : Erreur classification (quelle classe)
   - **dfl_loss** : Distribution focal loss (YOLO11)
   - **mAP50** : Mean Average Precision à IoU 0.5
   - **mAP50-95** : mAP moyenné sur IoU 0.5 à 0.95

5. **Attendre fin** ou cliquer "⏹️ STOP TRAINING" pour arrêter

### Durée Estimée

**Facteurs affectant la durée** :
- Nombre d'images
- Epochs
- Image size
- Batch size
- GPU vs CPU

**Exemples** :

| Configuration | Durée/epoch | 50 epochs |
|---------------|-------------|-----------|
| **500 images, 640px, batch 16, RTX 3060** | 2-3 min | 1h 40min-2h 30min |
| **500 images, 640px, batch 16, CPU** | 15-20 min | 12h 30min-16h 40min |
| **1000 images, 640px, batch 32, RTX 4070** | 3-4 min | 2h 30min-3h 20min |
| **200 images, 416px, batch 8, RTX 2060** | 45-60 sec | 37min-50min |

### Résultats de l'Entraînement

**Emplacement** : `runs/detect/train/` (ou `train2/`, `train3/`, etc. si multiples runs)

**Structure** :
```
runs/detect/train/
├── weights/
│   ├── best.pt          # Meilleur modèle (max mAP50-95)
│   └── last.pt          # Dernier modèle (epoch final)
├── results.png          # Graphiques métriques
├── results.csv          # Données CSV
├── confusion_matrix.png # Matrice de confusion
├── F1_curve.png         # Courbe F1-score
├── P_curve.png          # Courbe Precision
├── R_curve.png          # Courbe Recall
├── PR_curve.png         # Precision-Recall curve
├── args.yaml            # Arguments utilisés
└── train_batch*.jpg     # Exemples de batches d'entraînement
```

**Fichiers clés** :

1. **weights/best.pt** : **MODÈLE À UTILISER** pour détection
   - Sauvegardé à l'epoch avec meilleur mAP50-95
   - Copier vers `models/` pour utilisation permanente

2. **results.png** : Graphiques de toutes les métriques
   - train/box_loss, train/cls_loss, train/dfl_loss
   - val/box_loss, val/cls_loss, val/dfl_loss
   - metrics/precision, metrics/recall
   - metrics/mAP50, metrics/mAP50-95

3. **confusion_matrix.png** : Visualise erreurs de classification
   - Diagonale = prédictions correctes
   - Hors diagonale = confusions entre classes

### Évaluation des Résultats

**Métriques cibles** (bonnes performances) :

| Métrique | Excellent | Bon | Acceptable | Mauvais |
|----------|-----------|-----|------------|---------|
| **mAP50** | > 0.90 | 0.80-0.90 | 0.70-0.80 | < 0.70 |
| **mAP50-95** | > 0.70 | 0.60-0.70 | 0.50-0.60 | < 0.50 |
| **Precision** | > 0.90 | 0.80-0.90 | 0.70-0.80 | < 0.70 |
| **Recall** | > 0.85 | 0.75-0.85 | 0.65-0.75 | < 0.65 |

**Interpréter les résultats** :

✅ **Bon entraînement** :
- Courbes loss décroissantes et stables
- mAP50 > 0.80, mAP50-95 > 0.60
- Pas de grandes divergences train/val
- Matrice de confusion avec forte diagonale

⚠️ **Overfitting** (sur-apprentissage) :
- train_loss continue à descendre
- val_loss remonte ou stagne
- Grand écart train/val metrics
- **Solution** : Réduire epochs, augmenter augmentations

⚠️ **Underfitting** (sous-apprentissage) :
- train_loss et val_loss élevés
- mAP < 0.60 après 50+ epochs
- Courbes stagnent tôt
- **Solution** : Augmenter epochs, augmenter model size

### Resume Training (Reprendre entraînement)

**Si entraînement interrompu** :

1. **Vérifier** que `runs/detect/train/weights/last.pt` existe
2. **Activer** checkbox "Resume Training"
3. **Cliquer** "START TRAINING"
4. **L'entraînement reprend** à l'epoch où il s'était arrêté

**Commande équivalente** :
```bash
yolo task=detect mode=train model=runs/detect/train/weights/last.pt resume=True
```

### Bouton "📂 Open Results Folder"

Ouvre `runs/detect/train/` dans l'explorateur Windows pour voir tous les résultats.

---

## 14. 🔍 Détection Live

La vue **Detection** permet d'utiliser votre modèle entraîné pour **détecter des cartes en temps réel**.

### 3 Modes de Détection

#### 1. 📹 Webcam (Temps Réel)
- **Source** : Caméra du PC (webcam, caméra USB)
- **Usage** : Détection live de cartes physiques
- **FPS** : 15-60 FPS (selon GPU)

#### 2. 🎬 Video File
- **Source** : Fichier vidéo (MP4, AVI, MOV, etc.)
- **Usage** : Analyser vidéo pré-enregistrée
- **Sortie** : Vidéo annotée sauvegardée

#### 3. 🖼️ Image File
- **Source** : Image statique (PNG, JPG, WEBP)
- **Usage** : Détection sur photo unique
- **Sortie** : Image annotée sauvegardée

### Configuration

#### Model Path
- **Défaut** : `runs/detect/train/weights/best.pt`
- **Changeable** : Bouton "Browse" pour choisir autre modèle
- **Formats acceptés** : `.pt` (PyTorch)

**Modèles disponibles** :
- Votre modèle entraîné : `runs/detect/train/weights/best.pt`
- Modèle sauvegardé : `models/custom_model.pt`
- Modèle pré-entraîné : `yolov8n.pt` (détection générale COCO)

#### Confidence Threshold (Seuil de confiance)
- **Range** : 0.0-1.0 (slider)
- **Défaut** : 0.25 (25%)
- **Effet** :
  - 0.10-0.30 : Détecte presque tout (beaucoup de faux positifs)
  - 0.30-0.50 : Équilibre (recommandé)
  - 0.50-0.70 : Seulement détections sûres (peut manquer cartes)
  - 0.70-1.00 : Ultra-conservateur (très peu de détections)

#### IoU Threshold (Intersection over Union)
- **Range** : 0.0-1.0 (slider)
- **Défaut** : 0.45 (45%)
- **Effet** : Contrôle suppression des détections qui se chevauchent
  - 0.30-0.50 : Standard (recommandé)
  - 0.50-0.70 : Conservateur (garde plus de bbox proches)

#### Camera ID (Mode Webcam uniquement)
- **Range** : 0-9
- **Défaut** : 0 (webcam principale)
- **Usage** :
  - 0 : Webcam intégrée laptop
  - 1 : Première caméra USB externe
  - 2+ : Autres caméras si multi-caméras

#### Show Prices (Afficher les prix)
- **Checkbox** : ✅ Activer overlay des prix
- **Défaut** : Désactivé
- **Requis** : Base de données prix (`models/cards_database.yaml`)
- **Effet** : Affiche prix Cardmarket/TCGPlayer sur chaque carte détectée

**Exemple avec prix** :
```
┌─────────────────────┐
│ Pikachu (Class 0)   │
│ Conf: 0.94          │
│ 💰 €12.50 (CM)      │  ← Prix ajouté
└─────────────────────┘
```

### Lancement - Mode Webcam

1. **Configurer** :
   - Model : `runs/detect/train/weights/best.pt`
   - Confidence : 0.35
   - IoU : 0.45
   - Camera ID : 0
   - ✅ Show Prices (optionnel)

2. **Cliquer** "📹 START WEBCAM"

3. **Fenêtre de détection s'ouvre** :
   - Flux vidéo en direct
   - Bounding boxes colorées
   - Labels avec nom de classe + confiance
   - Prix (si activé)
   - FPS en haut à gauche

4. **Utilisation** :
   - Placer cartes devant caméra
   - Détections apparaissent en temps réel
   - Appuyer sur **'q'** pour quitter
   - Appuyer sur **'s'** pour screenshot

5. **Arrêt** : Appuyer **'q'** ou cliquer "⏹️ STOP DETECTION"

**FPS typiques** :
- RTX 3060 + YOLOv8n : 45-60 FPS
- RTX 2060 + YOLOv8n : 30-40 FPS
- CPU Intel i7 + YOLOv8n : 8-15 FPS

### Lancement - Mode Video

1. **Configurer** :
   - Model : `runs/detect/train/weights/best.pt`
   - Confidence : 0.35
   - IoU : 0.45

2. **Cliquer** "🎬 DETECT VIDEO"

3. **Sélectionner fichier vidéo** :
   - Formats : MP4, AVI, MOV, MKV, etc.
   - Parcourir et sélectionner

4. **Traitement** :
   - Progression affichée : Frame 245/1800 (13.6%)
   - Fenêtre preview en temps réel (optionnel)

5. **Sortie** :
   - Vidéo annotée : `output/detections/video_annotated.mp4`
   - Logs : Nombre de détections par frame
   - Statistiques finales

**Durée traitement** :
- Vidéo 1080p, 30 FPS, 1 minute, YOLOv8n, RTX 3060 : ~2-3 minutes
- Vidéo 720p, 60 FPS, 30 secondes, YOLOv8n, CPU : ~10-15 minutes

### Lancement - Mode Image

1. **Configurer** :
   - Model : `runs/detect/train/weights/best.pt`
   - Confidence : 0.35
   - IoU : 0.45
   - ✅ Show Prices

2. **Cliquer** "🖼️ DETECT IMAGE"

3. **Sélectionner image** :
   - Formats : PNG, JPG, JPEG, WEBP, BMP
   - Parcourir et sélectionner

4. **Détection instantanée** :
   - Image annotée affichée dans nouvelle fenêtre
   - Appuyer **'q'** pour fermer

5. **Sortie** :
   - Image annotée : `output/detections/image_annotated.png`
   - Logs : Détails de chaque détection

**Exemple de log** :
```
🔍 Detected 3 objects:
  - Class 0 (Pikachu): Conf 0.94, Bbox [120, 85, 305, 410]
    💰 Price: €12.50 (Cardmarket)
  - Class 1 (Charizard): Conf 0.89, Bbox [450, 120, 635, 445]
    💰 Price: €45.00 (Cardmarket)
  - Class 2 (Mewtwo): Conf 0.92, Bbox [780, 95, 965, 420]
    💰 Price: €28.00 (Cardmarket)
```

### Système de Prix (TCGdex + Base de Données)

#### Initialisation de la Base de Données

**Si `models/cards_database.yaml` n'existe pas** :

1. **Cliquer** "💰 Initialize Price Database"
2. **Sélectionner source** :
   - Option A : Depuis data.yaml existant
   - Option B : Depuis set TCGdex
3. **Traitement** :
   - Extraction des noms de cartes
   - Requêtes API TCGdex
   - Récupération prix Cardmarket + TCGPlayer
   - Sauvegarde dans `models/cards_database.yaml`

**Structure YAML** :
```yaml
cards:
  0:
    name: "Pikachu"
    set: "Surging Sparks"
    number: "025/191"
    price_cm: 12.50      # Cardmarket (EUR)
    price_tcp: 15.00     # TCGPlayer (USD)
    price_source: "TCGdex"
    last_updated: "2025-11-14"
  1:
    name: "Charizard"
    ...
```

#### Mise à Jour des Prix

**Pour actualiser les prix** :

1. **Cliquer** "🔄 Update Prices"
2. **Sélection** :
   - Toutes les cartes : Update all
   - Cartes spécifiques : Sélectionner class IDs
3. **Traitement** :
   - Requêtes API TCGdex
   - Mise à jour des prix dans YAML
   - Timestamp last_updated

**Fréquence recommandée** : 1× par semaine (prix TCG évoluent)

### Visualisation des Détections

**Éléments affichés** :

1. **Bounding Box** :
   - Couleur unique par classe
   - Épaisseur 2-3 pixels
   - Coins arrondis (optionnel)

2. **Label** :
   - Nom de la classe (ex: "Pikachu")
   - Confiance (ex: "0.94")
   - Format : `{class_name} {confidence:.2f}`

3. **Prix** (si activé) :
   - Devise : EUR (Cardmarket) ou USD (TCGPlayer)
   - Format : `💰 €12.50` ou `💰 $15.00`
   - Affiché sous le label

4. **FPS Counter** (mode webcam) :
   - Top-left corner
   - Format : `FPS: 45.2`

### Raccourcis Clavier (Détection Active)

| Touche | Action |
|--------|--------|
| **q** | Quitter détection |
| **s** | Screenshot (sauvegarde frame actuel) |
| **p** | Pause/Resume (vidéo uniquement) |
| **↑↓** | Ajuster confidence threshold |
| **Esc** | Quitter immédiatement |

### Troubleshooting Détection

**Problème** : Aucune détection
- ✅ Vérifier confidence threshold (essayer 0.10-0.20)
- ✅ Vérifier modèle chargé correct
- ✅ Vérifier éclairage (pas trop sombre)
- ✅ Vérifier cartes bien visibles (pas floues)

**Problème** : FPS trop bas (< 10)
- ✅ Réduire image size (416 au lieu de 640)
- ✅ Utiliser modèle plus léger (YOLOv8n au lieu de YOLOv8m)
- ✅ Fermer autres applications gourmandes
- ✅ Vérifier utilisation GPU (pas CPU)

**Problème** : Faux positifs
- ✅ Augmenter confidence threshold (0.50-0.70)
- ✅ Entraîner plus longtemps (plus d'epochs)
- ✅ Ajouter plus d'augmentations negatives

**Problème** : Prix non affichés
- ✅ Vérifier `models/cards_database.yaml` existe
- ✅ Vérifier class IDs correspondent entre modèle et YAML
- ✅ Initialiser/mettre à jour base de données prix

### Bouton "📂 Open Detections Folder"

Ouvre `output/detections/` dans l'explorateur Windows (screenshots et vidéos annotées).

---

## 15. 📦 Export Datasets

La vue **Export** permet d'exporter votre dataset YOLO vers **4 formats** de détection d'objets populaires.

### Pourquoi Exporter ?

**Cas d'usage** :
- ✅ **Entraîner sur autre plateforme** : Roboflow, Azure Custom Vision, AWS SageMaker
- ✅ **Frameworks différents** : TensorFlow Object Detection API, Detectron2
- ✅ **Partager dataset** : Format universel (COCO JSON)
- ✅ **Archive/backup** : Format standardisé

### 4 Formats Supportés

#### 1. 🔷 COCO JSON
- **Description** : Common Objects in Context (2014)
- **Framework** : TensorFlow, Detectron2, MMDetection
- **Usage** : Standard industriel
- **Fichiers générés** :
  ```
  output/export_coco/
  ├── annotations/
  │   ├── instances_train.json
  │   ├── instances_val.json
  │   └── instances_test.json (optionnel)
  ├── train/
  │   └── *.jpg (images)
  ├── val/
  │   └── *.jpg
  └── dataset_info.json
  ```

**Structure JSON** :
```json
{
  "images": [
    {
      "id": 1,
      "file_name": "pikachu_001.jpg",
      "width": 640,
      "height": 640,
      "license": 1,
      "flickr_url": "",
      "coco_url": "",
      "date_captured": "2025-11-14"
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [120, 85, 185, 325],  # [x, y, width, height]
      "area": 60125,
      "segmentation": [],
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 0,
      "name": "Pikachu",
      "supercategory": "pokemon"
    }
  ]
}
```

**Avantages** :
- ✅ Standard le plus utilisé (2014-present)
- ✅ Supporte segmentation + détection
- ✅ Compatible avec COCO metrics (mAP)

**Inconvénients** :
- ❌ Format JSON volumineux (> 100 MB pour gros datasets)

#### 2. 🔶 Pascal VOC XML
- **Description** : Visual Object Classes (2005-2012)
- **Framework** : PyTorch, torchvision, anciens projets
- **Usage** : Legacy mais encore utilisé
- **Fichiers générés** :
  ```
  output/export_voc/
  ├── Annotations/
  │   ├── pikachu_001.xml
  │   ├── pikachu_002.xml
  │   └── ...
  ├── JPEGImages/
  │   ├── pikachu_001.jpg
  │   ├── pikachu_002.jpg
  │   └── ...
  ├── ImageSets/
  │   └── Main/
  │       ├── train.txt
  │       ├── val.txt
  │       └── test.txt
  └── labels.txt
  ```

**Structure XML** :
```xml
<annotation>
  <folder>JPEGImages</folder>
  <filename>pikachu_001.jpg</filename>
  <path>C:\DATA\pok\output\export_voc\JPEGImages\pikachu_001.jpg</path>
  <source>
    <database>Pokemon Dataset</database>
  </source>
  <size>
    <width>640</width>
    <height>640</height>
    <depth>3</depth>
  </size>
  <segmented>0</segmented>
  <object>
    <name>Pikachu</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
      <xmin>120</xmin>
      <ymin>85</ymin>
      <xmax>305</xmax>
      <ymax>410</ymax>
    </bndbox>
  </object>
</annotation>
```

**Avantages** :
- ✅ Un fichier XML par image (facile à manipuler)
- ✅ Format lisible par humain
- ✅ Compatible avec torchvision VOC dataset

**Inconvénients** :
- ❌ Format ancien (2005-2012)
- ❌ Beaucoup de fichiers (1 XML par image)

#### 3. 🔷 TFRecord (TensorFlow)
- **Description** : Format binaire TensorFlow
- **Framework** : TensorFlow Object Detection API
- **Usage** : Production TensorFlow (TF-Serving, TFLite)
- **Fichiers générés** :
  ```
  output/export_tfrecord/
  ├── train.record          # TFRecord binaire
  ├── val.record
  ├── test.record (optionnel)
  ├── label_map.pbtxt       # Protobuf text
  └── pipeline.config       # Config TF Object Detection API
  ```

**Structure label_map.pbtxt** :
```protobuf
item {
  id: 1
  name: 'Pikachu'
  display_name: 'Pikachu'
}
item {
  id: 2
  name: 'Charizard'
  display_name: 'Charizard'
}
```

**Avantages** :
- ✅ Lecture ultra-rapide (binaire optimisé)
- ✅ Intégration TensorFlow native
- ✅ Supporte TFLite (mobile/edge)

**Inconvénients** :
- ❌ Format binaire non lisible
- ❌ Nécessite TensorFlow pour lire

#### 4. 🔵 Roboflow
- **Description** : Format cloud Roboflow
- **Framework** : Roboflow Universe (YOLOv5-v8, etc.)
- **Usage** : Import direct sur Roboflow.com
- **Fichiers générés** :
  ```
  output/export_roboflow/
  ├── train/
  │   ├── images/
  │   │   └── *.jpg
  │   └── labels/
  │       └── *.txt (format YOLO)
  ├── val/
  │   ├── images/
  │   └── labels/
  ├── test/ (optionnel)
  │   ├── images/
  │   └── labels/
  ├── data.yaml
  └── README.roboflow.txt
  ```

**Structure data.yaml** :
```yaml
train: train/images
val: val/images
test: test/images
nc: 3
names: ['Pikachu', 'Charizard', 'Mewtwo']
roboflow:
  workspace: your-workspace
  project: pokemon-dataset
  version: 1
```

**Avantages** :
- ✅ Upload direct sur Roboflow (génère lien API)
- ✅ Augmentations cloud disponibles
- ✅ Versioning automatique

**Inconvénients** :
- ❌ Nécessite compte Roboflow (gratuit avec limites)

### Configuration Export

#### Dataset Path
- **Défaut** : `output/balanced/` (si balancé) ou `output/mosaics/`
- **Requis** : Dataset YOLO valide (images/ + labels/ + data.yaml)
- **Changeable** : Bouton "Browse"

#### Export Format
- **Radio buttons** : Sélectionner 1 format parmi 4
  - 🔷 COCO JSON
  - 🔶 Pascal VOC
  - 🔷 TFRecord
  - 🔵 Roboflow

#### Output Directory
- **Défaut** : `output/export_{format}/` (auto-généré)
- **Changeable** : Bouton "Browse"

#### Split Ratios (Proportions train/val/test)
- **Train** : 0-100% (slider, défaut 70%)
- **Val** : 0-100% (slider, défaut 20%)
- **Test** : 0-100% (slider, défaut 10%)
- **Contrainte** : Train + Val + Test = 100%

**Recommandations** :

| Dataset Size | Train | Val | Test | Justification |
|--------------|-------|-----|------|---------------|
| **< 500 images** | 80% | 20% | 0% | Pas assez pour test set |
| **500-2000** | 70% | 20% | 10% | Standard (recommandé) |
| **2000-5000** | 70% | 15% | 15% | Plus de test data |
| **> 5000** | 80% | 10% | 10% | Beaucoup de data |

#### Include Augmented Images
- **Checkbox** : ✅ Inclure images augmentées
- **Défaut** : Activé
- **Effet** : Exporte aussi images générées par augmentation (pas uniquement originales)

#### Preserve Structure
- **Checkbox** : ✅ Préserver structure de dossiers
- **Défaut** : Activé
- **Effet** : Garde organisation par classes si elle existe

### Lancement de l'Export

1. **Sélectionner** Dataset Path : `output/balanced/`
2. **Choisir** format : COCO JSON (par exemple)
3. **Configurer** splits : 70% train, 20% val, 10% test
4. **Activer** "Include Augmented"
5. **Cliquer** "📦 START EXPORT"

**Progression** :
```
📦 Exporting to COCO JSON format...
✅ Reading YOLO dataset: 1248 images found
📋 Creating splits: Train (874), Val (250), Test (124)
📝 Generating COCO JSON annotations...
  - Processing train split... 874/874 ━━━━━━━━ 100%
  - Processing val split... 250/250 ━━━━━━━━ 100%
  - Processing test split... 124/124 ━━━━━━━━ 100%
💾 Saving annotations: instances_train.json (15.2 MB)
💾 Saving annotations: instances_val.json (4.3 MB)
💾 Saving annotations: instances_test.json (2.1 MB)
✅ Export completed in 1m 23s
📂 Output: output/export_coco/
```

### Durée Estimée

| Dataset Size | Format | Durée |
|--------------|--------|-------|
| 500 images | COCO | 30-45 sec |
| 500 images | VOC | 45-60 sec (1 XML/image) |
| 500 images | TFRecord | 1-2 min (écriture binaire) |
| 1000 images | COCO | 1-1.5 min |
| 1000 images | TFRecord | 2-3 min |
| 5000 images | COCO | 5-8 min |

### Vérification Post-Export

**Checklist** :

✅ **Vérifier structure** :
```bash
# COCO
output/export_coco/
  ├── annotations/instances_train.json (existe)
  ├── train/ (874 images)
  └── val/ (250 images)

# VOC
output/export_voc/
  ├── Annotations/ (1248 XML files)
  └── JPEGImages/ (1248 JPG files)
```

✅ **Vérifier nombres** :
- Nombre images = nombre annotations
- Train + Val + Test = Total original
- Splits respectent ratios (±1%)

✅ **Tester avec framework** :
```python
# COCO
from pycocotools.coco import COCO
coco = COCO('output/export_coco/annotations/instances_train.json')
print(f"Images: {len(coco.getImgIds())}")
print(f"Categories: {len(coco.getCatIds())}")

# VOC
import xml.etree.ElementTree as ET
tree = ET.parse('output/export_voc/Annotations/pikachu_001.xml')
root = tree.getroot()
print(f"Objects: {len(root.findall('object'))}")
```

### Bouton "📂 Open Export Folder"

Ouvre le dossier d'export (`output/export_{format}/`) dans l'explorateur Windows.

---

## 16. 🔧 Outils & Utilitaires

La vue **Tools** propose **4 utilitaires** pour gérer votre projet.

### 1. 📊 Excel & Prices Manager

**But** : Gérer les prix des cartes (Excel ou YAML).

#### Initialiser Excel de Prix
1. **Cliquer** "📋 Create Excel Template"
2. **Fichier généré** : `excel/cards_prices.xlsx`
3. **Structure** :

| Class ID | Card Name | Set | Number | Price (Cardmarket) | Price (TCGPlayer) | Last Updated |
|----------|-----------|-----|--------|-------------------|-------------------|--------------|
| 0 | Pikachu | Surging Sparks | 025/191 | 12.50 | 15.00 | 2025-11-14 |
| 1 | Charizard | Obsidian Flames | 006/197 | 45.00 | 52.00 | 2025-11-14 |

4. **Remplir manuellement** ou **importer depuis TCGdex**

#### Importer depuis TCGdex
1. **Cliquer** "🌐 Import from TCGdex"
2. **Sélectionner set** : Surging Sparks (dropdown)
3. **Traitement** :
   - Récupération liste cartes
   - Requêtes API prix
   - Remplissage Excel automatique
4. **Durée** : 30-60 sec (selon nombre de cartes)

#### Convertir Excel → YAML
1. **Cliquer** "🔄 Convert Excel to YAML"
2. **Fichier généré** : `models/cards_database.yaml`
3. **Usage** : Utilisé par détection pour afficher prix

#### Mettre à Jour Prix
1. **Cliquer** "🔄 Update Prices"
2. **Options** :
   - Toutes les cartes
   - Seulement cartes > 7 jours
3. **Requêtes API** → mise à jour Excel/YAML

---

### 2. 🌐 TCG Browser

**But** : Explorer l'API TCGdex visuellement.

#### Navigation
1. **Cliquer** "🌐 Open TCG Browser"
2. **Fenêtre s'ouvre** avec :
   - Liste des sets (dropdown)
   - Grille de cartes (images)
   - Détails de carte (clic sur image)

#### Détails Affichés
- Nom de la carte
- Set + numéro
- Type(s)
- HP
- Rareté
- Prix Cardmarket / TCGPlayer
- Image haute résolution

#### Export depuis Browser
- **Clic droit** sur carte → "Download"
- **Sélection multiple** → "Download Selected"
- **Télécharge** dans `images/{set_name}/`

---

### 3. 🗑️ Clean & Reset

**But** : Nettoyer les fichiers temporaires et reset l'environnement.

#### Clean Temporary Files
**Cliquer** "🧹 Clean Temp Files"

**Supprime** :
- `__pycache__/` (tous dossiers)
- `*.pyc` (bytecode Python)
- `.pytest_cache/`
- `runs/detect/train*/` (anciens runs sauf dernier)
- `output/detections/*.mp4` (vidéos temporaires)

**Espace libéré** : 100 MB - 2 GB

#### Reset Configuration
**Cliquer** "🔄 Reset to Defaults"

**Réinitialise** :
- `config/gui_config.json` → valeurs par défaut
- Paramètres UI (batch size, epochs, etc.)
- Ne touche PAS aux images/datasets

**Confirmation requise** : ⚠️ "Are you sure?"

#### Deep Clean (Advanced)
**Cliquer** "⚠️ Deep Clean" (bouton rouge)

**Supprime TOUT** :
- `images/` (toutes images téléchargées)
- `output/` (tous datasets)
- `runs/` (tous entraînements)
- `models/*.pt` (modèles entraînés)
- **⚠️ IRRÉVERSIBLE** - Demande mot de passe confirmation

---

### 4. 📈 Statistics & Reports

**But** : Générer rapports sur votre projet.

#### Project Statistics
**Cliquer** "📊 Generate Report"

**Génère** : `output/project_report.html`

**Contenu** :
- **Images** : Total, par set, par langue
- **Dataset** : Train/val splits, distribution classes
- **Augmentation** : Techniques utilisées, nombres
- **Mosaïques** : Modes, layouts, total généré
- **Entraînement** : Modèles, epochs, best mAP
- **Détections** : Nombre de détections, classes détectées

**Visualisations** :
- Graphiques distribution classes (bar chart)
- Courbes d'entraînement (line chart)
- Matrice de confusion (heatmap)
- Timeline du projet (Gantt)

#### Export Project Archive
**Cliquer** "📦 Create Archive"

**Crée** : `pokemon_dataset_backup_2025-11-14.zip`

**Contenu** :
- `config/` (configurations)
- `models/` (modèles + mappings)
- `excel/` (prix)
- `output/balanced/` (dataset final)
- `runs/detect/train/weights/best.pt` (meilleur modèle)
- **Exclut** : images/, runs/detect/train2-10/

**Taille** : 50-500 MB

---

## 17. ⚙️ Settings - 8 Tabs Détaillés

La vue **Settings** propose **8 tabs** de configuration avancée (v3.2.4).

### Tab 1 : ⚙️ General

#### Langue / Language
- **Options** : Français, English, Español, Deutsch, Italiano, 日本語
- **Défaut** : Français
- **Effet** : Traduction UI complète (redémarrage requis)

#### Thème / Theme
- **Options** : Catppuccin Mocha (défaut), Light, High Contrast
- **Effet** : Change palette de couleurs UI

#### Auto-Save Configuration
- **Checkbox** : ✅ Sauvegarder config automatiquement
- **Défaut** : Activé
- **Effet** : gui_config.json mis à jour à chaque modification

#### Check Updates on Startup
- **Checkbox** : ✅ Vérifier mises à jour au lancement
- **Défaut** : Activé
- **Effet** : Requête GitHub API pour dernière version

#### Default Working Directory
- **Path** : Dossier racine projet
- **Défaut** : Dossier actuel
- **Changeable** : Bouton "Browse"

---

### Tab 2 : 🎨 Augmentation Settings

#### Default Augmentation Count
- **Range** : 1-20
- **Défaut** : 5
- **Effet** : Nombre d'images augmentées par original (vue Augmentation)

#### Enable GPU Acceleration (Albumentations)
- **Checkbox** : ✅ Accélération GPU Albumentations
- **Défaut** : Activé
- **Note** : Albumentations utilise automatiquement le GPU via OpenCV-CUDA si disponible

#### Techniques Defaults (22 sliders)
- **Brightness** : -50 à +50 (défaut ±30)
- **Contrast** : 0.5-1.5 (défaut 0.7-1.3)
- **Saturation** : 0.5-1.5 (défaut 0.7-1.3)
- **Hue** : -30 à +30 (défaut ±20)
- **Gaussian Blur** : 0-5 sigma (défaut 0-2)
- **Sharpen** : 0.0-2.0 (défaut 0-1)
- **Gaussian Noise** : 0-0.05 (défaut 0-0.03)
- **Dropout** : 0-0.1 (défaut 0-0.05)
- **Coarse Dropout** : 0-0.15 (défaut 0-0.1)
- **Rotate** : -180 à +180 (défaut ±15)
- **Affine Scale** : 0.8-1.2 (défaut 0.9-1.1)
- **Affine Shear** : -20 à +20 (défaut ±10)
- **Affine Translate** : -20% à +20% (défaut ±10%)
- **Perspective** : 0.0-0.1 (défaut 0.0-0.05)
- **Elastic Transform** : alpha 0-50 (défaut 0-30), sigma 3-7 (défaut 4-6)
- **Piecewise Affine** : 0.0-0.05 (défaut 0.0-0.03)
- **Flip Horizontal** : 0-100% (défaut 50%)
- **Flip Vertical** : 0-100% (défaut 0%)
- **CLAHE** : clip 1-4 (défaut 1-2)
- **Motion Blur** : kernel 3-15 (défaut 3-7)
- **Cutout** : nombre 0-5 (défaut 0-3), taille 10-50px (défaut 10-30px)
- **Random Erasing** : probabilité 0-1 (défaut 0.5)

---

### Tab 3 : 🖼️ Mosaic Settings

#### Default Mosaic Mode
- **Options** : Quick, Standard, Complete
- **Défaut** : Standard

#### Default Layout
- **Options** : Grid, Rotation, Random
- **Défaut** : Grid

#### Default Background Mode
- **Options** : Mosaic, Local, Web
- **Défaut** : Mosaic

#### Mosaic Count (Quick Mode)
- **Range** : 1-1000
- **Défaut** : 50

#### Use Optimized Engine (v3.2.1)
- **Checkbox** : ✅ Utiliser moteur optimisé
- **Défaut** : Activé (30-60× plus rapide)

#### Generate Fake Backgrounds
- **Checkbox** : ✅ Générer fonds fake automatiquement
- **Défaut** : Activé

#### Fake Background Count
- **Range** : 10-500
- **Défaut** : 50

---

### Tab 4 : 🎓 Training Settings

#### Default Model
- **Options** : YOLOv8n, YOLOv8s, YOLOv8m, YOLOv8l, YOLOv8x, YOLO11n, YOLO11s
- **Défaut** : YOLOv8n

#### Default Epochs
- **Range** : 1-1000
- **Défaut** : 50

#### Default Batch Size
- **Range** : 1-64
- **Défaut** : 16 (auto-détecté selon VRAM)

#### Default Image Size
- **Options** : 320, 416, 512, 640, 800, 1024, 1280
- **Défaut** : 640

#### Use Mixed Precision (FP16)
- **Checkbox** : ✅ Entraînement FP16
- **Défaut** : Activé (RTX 20xx/30xx/40xx)
- **Effet** : 2× plus rapide, 2× moins VRAM

#### Save Best Only
- **Checkbox** : ✅ Sauver uniquement best.pt
- **Défaut** : Désactivé (sauve aussi last.pt)

#### Patience (Early Stopping)
- **Range** : 0-100 (0 = désactivé)
- **Défaut** : 20 epochs
- **Effet** : Arrête si mAP ne s'améliore pas pendant N epochs

---

### Tab 5 : 🔍 Detection Settings

#### Default Confidence
- **Range** : 0.0-1.0
- **Défaut** : 0.25

#### Default IoU
- **Range** : 0.0-1.0
- **Défaut** : 0.45

#### Show FPS Counter
- **Checkbox** : ✅ Afficher FPS (webcam)
- **Défaut** : Activé

#### Show Prices by Default
- **Checkbox** : ❌ Afficher prix automatiquement
- **Défaut** : Désactivé

#### Save Detection Results
- **Checkbox** : ✅ Sauvegarder résultats
- **Défaut** : Activé
- **Effet** : Screenshots/vidéos dans `output/detections/`

#### Max Detection Time (Webcam)
- **Range** : 0-3600 secondes (0 = illimité)
- **Défaut** : 0 (pas de limite)

---

### Tab 6 : 📦 Export Settings

#### Default Export Format
- **Options** : COCO, VOC, TFRecord, Roboflow
- **Défaut** : COCO

#### Default Train Split
- **Range** : 0-100%
- **Défaut** : 70%

#### Default Val Split
- **Range** : 0-100%
- **Défaut** : 20%

#### Default Test Split
- **Range** : 0-100%
- **Défaut** : 10%

#### Include Augmented by Default
- **Checkbox** : ✅ Inclure augmentations
- **Défaut** : Activé

#### Generate Dataset Report
- **Checkbox** : ✅ Générer rapport HTML
- **Défaut** : Activé

---

### Tab 7 : 🚀 Advanced Settings

#### Enable Debug Mode
- **Checkbox** : ❌ Mode debug (logs verbeux)
- **Défaut** : Désactivé

#### Enable Performance Monitoring
- **Checkbox** : ✅ Monitoring performances
- **Défaut** : Activé
- **Effet** : Logs temps d'exécution fonctions

#### Max Parallel Downloads
- **Range** : 1-20
- **Défaut** : 5 (threads parallèles TCGdex)

#### GPU Memory Fraction
- **Range** : 0.1-1.0
- **Défaut** : 0.9 (90% VRAM disponible)

#### Enable Augmentation Cache
- **Checkbox** : ✅ Cacher pipelines Albumentations
- **Défaut** : Activé (gain 10-20%)

#### Clear Cache on Exit
- **Checkbox** : ❌ Vider cache à la fermeture
- **Défaut** : Désactivé

---

### Tab 8 : 🐛 Debug & Logs

#### Log Level
- **Options** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Défaut** : INFO

#### Log to File
- **Checkbox** : ✅ Sauvegarder logs dans fichier
- **Défaut** : Activé
- **Fichier** : `logs/app.log`

#### Show Timestamps in Logs
- **Checkbox** : ✅ Afficher timestamps
- **Défaut** : Activé

#### Enable Console Output
- **Checkbox** : ✅ Afficher logs dans console
- **Défaut** : Activé

#### Max Log File Size
- **Range** : 1-100 MB
- **Défaut** : 10 MB

#### Log Rotation
- **Checkbox** : ✅ Rotation automatique
- **Défaut** : Activé (garde 5 derniers fichiers)

---

### Boutons Settings

**💾 Save Settings** : Sauvegarde toutes modifications dans `config/gui_config.json`

**🔄 Reset to Defaults** : Restaure valeurs par défaut (confirmation requise)

**📂 Open Config File** : Ouvre `config/gui_config.json` dans éditeur texte

---

## 18. 📋 Fichiers de Configuration

### 1. gui_config.json

**Emplacement** : `config/gui_config.json`

**Contenu** : Tous les settings UI (8 tabs)

**Structure** :
```json
{
  "general": {
    "language": "fr",
    "theme": "catppuccin_mocha",
    "auto_save": true,
    "check_updates": true,
    "default_working_dir": "C:\\DATA\\pok"
  },
  "augmentation": {
    "default_count": 5,
    "gpu_acceleration": false,
    "techniques": {
      "brightness": {"min": -30, "max": 30},
      "contrast": {"min": 0.7, "max": 1.3},
      ...
    }
  },
  "mosaic": {
    "default_mode": "standard",
    "default_layout": "grid",
    "default_background": "mosaic",
    "use_optimized": true,
    "fake_background_count": 50
  },
  "training": {
    "default_model": "yolov8n",
    "default_epochs": 50,
    "default_batch_size": 16,
    "default_image_size": 640,
    "use_fp16": true,
    "patience": 20
  },
  "detection": {
    "default_confidence": 0.25,
    "default_iou": 0.45,
    "show_fps": true,
    "show_prices": false,
    "save_results": true
  },
  "export": {
    "default_format": "coco",
    "train_split": 0.7,
    "val_split": 0.2,
    "test_split": 0.1,
    "include_augmented": true
  },
  "advanced": {
    "debug_mode": false,
    "performance_monitoring": true,
    "max_parallel_downloads": 5,
    "gpu_memory_fraction": 0.9
  },
  "logging": {
    "level": "INFO",
    "to_file": true,
    "show_timestamps": true,
    "max_file_size_mb": 10,
    "rotation": true
  }
}
```

---

### 2. paths.json (optionnel)

**Emplacement** : `config/paths.json`

**But** : Personnaliser chemins si structure modifiée

**Structure** :
```json
{
  "images": "C:\\CustomFolder\\images",
  "output": "D:\\Datasets\\output",
  "models": "C:\\DATA\\pok\\models",
  "excel": "C:\\DATA\\pok\\excel",
  "runs": "C:\\DATA\\pok\\runs"
}
```

---

### 3. api_config.json

**Emplacement** : `config/api_config.json`

**But** : Configuration API TCGdex

**Structure** :
```json
{
  "tcgdex": {
    "base_url": "https://api.tcgdex.net/v2/en",
    "timeout": 10,
    "retry": 3,
    "languages": ["en", "fr", "de", "es", "it", "pt", "ja", "ko", "zh-tw", "pl"],
    "cache_expiry_days": 7
  },
  "cardmarket": {
    "enabled": true,
    "currency": "EUR"
  },
  "tcgplayer": {
    "enabled": true,
    "currency": "USD"
  }
}
```

---

## 19. ❓ FAQ & Troubleshooting

### Installation & Dépendances

**Q : Erreur "NumPy 2.0 incompatible" ?**
```
A : imgaug nécessite NumPy < 2.0
Solution:
  pip uninstall numpy
  pip install "numpy<2.0"
```

**Q : "CUDA not available" mais j'ai une GPU NVIDIA ?**
```
A : PyTorch CPU installé ou drivers NVIDIA manquants
Solution:
  # Vérifier GPU
  python -c "import torch; print(torch.cuda.is_available())"
  
  # Réinstaller PyTorch GPU
  pip uninstall torch torchvision
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

**Q : Installation bloquée sur "Building wheels for opencv-python" ?**
```
A : Compilation OpenCV longue (5-10 min sur CPU ancien)
Solution: Patienter ou installer OpenCV pre-built
  pip install opencv-python-headless
```

---

### GUI & Utilisation

**Q : Interface ne répond plus pendant augmentation ?**
```
A : Traitement bloque UI (tkinter single-threaded)
Solution: Attendre fin ou utiliser CLI pour gros batches
```

**Q : "UnicodeEncodeError" dans logs Windows ?**
```
A : Caractères spéciaux Pokémon (é, ñ, etc.)
Solution: Vérifier PYTHONIOENCODING=utf-8 dans START.bat
```

**Q : Bouton "START" grisé ?**
```
A : Validation échouée (champ vide ou chemin invalide)
Solution: Vérifier tous les champs requis remplis
```

---

### Téléchargement d'Images

**Q : Erreur "429 Too Many Requests" TCGdex ?**
```
A : Rate limit API atteint
Solution: Attendre 1-2 min ou réduire parallel downloads (Settings)
```

**Q : Images téléchargées mais dossier vide ?**
```
A : Erreur réseau silencieuse
Solution: Vérifier logs (logs/app.log) et connexion internet
```

**Q : Certaines cartes manquantes ?**
```
A : Pas disponibles sur TCGdex ou set incomplet
Solution: Télécharger set différent ou ajouter images manuellement
```

---

### Augmentation

**Q : Augmentation très lente (1 image/10 sec) ?**
```
A : CPU lent + augmentations lourdes (ElasticTransform)
Solution: Désactiver Elastic/PiecewiseAffine ou réduire intensité
```

**Q : Images augmentées floues ?**
```
A : GaussianBlur + MotionBlur activés ensemble
Solution: Réduire sigma blur ou désactiver l'un des deux
```

**Q : Bounding boxes débordent après rotation ?**
```
A : Rotation > ±30° peut sortir bbox du cadre
Solution: Limiter rotation à ±15° (recommandé)
```

---

### Mosaïques

**Q : "No valid background images found" ?**
```
A : Dossier backgrounds/ vide
Solution: Placer images JPG/PNG dans backgrounds/ ou utiliser mode Web
```

**Q : Mosaïque génération bloquée à 0% ?**
```
A : Erreur dans image_downloader (pas d'images source)
Solution: Vérifier images/ contient au moins 1 carte
```

**Q : Mosaïques lentes malgré optimizations v3.2.1 ?**
```
A : Mode "Complete" avec 1000+ images
Solution: Utiliser mode "Standard" ou "Quick" pour datasets massifs
```

---

### Entraînement

**Q : "RuntimeError: CUDA out of memory" ?**
```
A : Batch size trop élevé pour VRAM disponible
Solution: Réduire batch size (16 → 8 → 4)
```

**Q : mAP stagne à 0.30 après 50 epochs ?**
```
A : Dataset insuffisant ou trop peu varié
Solution:
  1. Augmenter augmentations (10-20 par image)
  2. Générer plus de mosaïques
  3. Vérifier distribution classes équilibrée
```

**Q : "nan" loss après quelques epochs ?**
```
A : Learning rate trop élevé ou gradient explosion
Solution: Arrêter et réduire batch size ou utiliser modèle plus petit
```

---

### Détection

**Q : Aucune détection sur webcam ?**
```
A : Confidence threshold trop élevé ou modèle non adapté
Solution:
  1. Réduire confidence à 0.10-0.15
  2. Vérifier modèle entraîné correct
  3. Vérifier éclairage (pas trop sombre)
```

**Q : FPS très bas (< 5) ?**
```
A : CPU mode ou modèle lourd
Solution:
  1. Vérifier GPU utilisé (pas CPU)
  2. Utiliser YOLOv8n (plus rapide)
  3. Réduire image size (416 au lieu de 640)
```

**Q : Prix non affichés ?**
```
A : Base de données prix manquante
Solution: Initialiser prix (Tools → Excel & Prices → Initialize)
```

---

### Divers

**Q : Comment transférer projet sur autre PC ?**
```
A : Archiver projet
Solution:
  1. Tools → Statistics & Reports → Create Archive
  2. Copier .zip sur autre PC
  3. Extraire et installer dépendances (INSTALL.bat)
```

**Q : Logs trop verbeux ?**
```
A : Log level DEBUG activé
Solution: Settings → Debug & Logs → Log Level → INFO
```

**Q : Comment réinitialiser complètement ?**
```
A : Deep Clean + Reset
Solution:
  1. Tools → Clean & Reset → Deep Clean (⚠️ supprime tout)
  2. Settings → Reset to Defaults
  3. Redémarrer app
```

---

## 20. 📚 Cas d'Usage Courants

### Cas 1 : Débutant - Premier Dataset (200 cartes)

**Objectif** : Créer premier dataset YOLO simple

**Étapes** :
1. **Télécharger images** (View: Image Download)
   - Set: Surging Sparks
   - Language: English
   - Count: 200
   - Duration: 5-10 min

2. **Augmentation légère** (View: Augmentation)
   - Count: 3 augmentations/image
   - Techniques: Brightness, Rotation, Flip Horizontal
   - Duration: 15-20 min

3. **Mosaïques rapides** (View: Mosaics)
   - Mode: Quick
   - Count: 50
   - Background: Mosaic
   - Duration: 1-2 min (v3.2.1 optimisé)

4. **Entraînement test** (View: Training)
   - Model: YOLOv8n
   - Epochs: 20
   - Batch: 8
   - Duration: 40-60 min (GPU) / 6-8h (CPU)

5. **Détection test** (View: Detection)
   - Mode: Image
   - Tester sur quelques images

**Résultat attendu** :
- Dataset ~650 images (200 originales + 600 augmentées + 50 mosaïques)
- mAP50 : 0.60-0.75 (correct pour début)
- Temps total : 1-2h (GPU) / 8-10h (CPU)

---

### Cas 2 : Production - Dataset Compétitif (500 cartes)

**Objectif** : Dataset pour production/compétition

**Étapes** :
1. **Télécharger multi-sets** (View: Image Download)
   - Sets: Surging Sparks, Obsidian Flames, Paldea Evolved
   - Languages: English, French
   - Count: ~500 cartes uniques
   - Duration: 20-30 min

2. **Augmentation intensive** (View: Augmentation)
   - Count: 10 augmentations/image
   - Toutes techniques activées
   - Duration: 1-2h

3. **Validation dataset** (View: Validation)
   - Checks: Image integrity, labels, distribution
   - Correction erreurs
   - Duration: 10-15 min

4. **Auto-Balancing** (View: Auto-Balancing)
   - Strategy: Combined
   - Target: 100 images/class
   - Duration: 30-60 min

5. **Mosaïques complètes** (View: Mosaics)
   - Mode: Complete
   - Layouts: Grid + Rotation + Random
   - Backgrounds: Mosaic + Local
   - Duration: 5-10 min (v3.2.1)

6. **Entraînement complet** (View: Training)
   - Model: YOLOv8m ou YOLO11s
   - Epochs: 100-150
   - Batch: 16-32 (selon GPU)
   - Duration: 3-5h (RTX 3060)

7. **Détection validation** (View: Detection)
   - Mode: Webcam + Video
   - Tester scénarios réels

8. **Export multi-format** (View: Export)
   - COCO (pour archive)
   - Roboflow (pour partage)

**Résultat attendu** :
- Dataset ~6000 images (500 originales + 5000 augmentées + 500 mosaïques)
- mAP50 : 0.85-0.95 (production-ready)
- Temps total : 5-8h (GPU puissant)

---

### Cas 3 : Test Rapide - Workflow Automatique

**Objectif** : Tester toute pipeline rapidement

**Étapes** :
1. **Cliquer** "Workflow Automatique" (View: Workflow)
2. **Configurer** :
   - Download: Surging Sparks, 50 cartes
   - Augmentation: 2 images/carte
   - Mosaics: Quick mode, 20 mosaïques
   - Training: YOLOv8n, 10 epochs
3. **Lancer** : Automatique end-to-end
4. **Duration** : 1-2h total

**Résultat attendu** :
- Dataset ~120 images
- mAP50 : 0.40-0.60 (normal pour 10 epochs)
- Validation complète du workflow

---

**FIN DU GUIDE UTILISATEUR**

**Version** : 3.2  
**Total lignes** : ~8700 lignes  
**Dernière mise à jour** : 14 novembre 2025
