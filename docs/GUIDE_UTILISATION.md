# 📚 GUIDE D'UTILISATION - Générateur de Dataset Pokémon

## 🎯 Vue d'ensemble

Ce projet permet de générer des datasets d'images de cartes Pokémon augmentées et organisées en mosaïques pour l'entraînement de modèles YOLO.

---

## 🚀 Installation

### Prérequis
- **Python 3.12** (obligatoire, pas 3.13)
- Windows 10/11

### Installation de l'environnement
```batch
.\install_env.bat
```

Ce script va :
- Créer un environnement virtuel `.venv`
- Installer toutes les dépendances (NumPy, OpenCV, imgaug, etc.)
- Vérifier la compatibilité Python 3.12

---

## 📁 Structure des dossiers

```
Pokemons/
├── images/                    # Images originales de cartes Pokémon
├── fakeimg/                   # Images de fond pour les mosaïques
├── output/
│   ├── augmented/            # Images augmentées (générées par augmentation.py)
│   │   ├── images/           # Images augmentées
│   │   ├── labels/           # Annotations YOLO
│   │   └── data.yaml         # Configuration YOLO
│   └── yolov8/               # Mosaïques (générées par mosaic.py)
│       ├── images/           # Images de mosaïques
│       ├── labels/           # Annotations YOLO des mosaïques
│       ├── data.yaml         # Configuration YOLO
│       └── annotations.json  # Annotations détaillées
├── cards_info.xlsx           # Informations des cartes (Set #, Name)
└── .venv/                    # Environnement virtuel Python
```

---

## ⬇️ 0. TÉLÉCHARGEMENT D'IMAGES (NOUVEAU)

### 📦 Via GUI v3.0

**Vue: ⬇️ Image Download**

Téléchargez directement des sets de cartes Pokemon depuis l'API TCGdex (gratuite, sans authentification).

**Paramètres:**
- **Pokemon Set**: Sélectionnez un set populaire dans le menu déroulant ou saisissez manuellement un nom/ID de set
  - Exemples: "Surging Sparks (sv08)", "Stellar Crown (sv07)", "base1", "swsh1"
- **Language**: Langue des cartes (English, Français, Deutsch, Italiano, Español, Português, 日本語, 한국어, 中文, ไทย)
- **Quality**: `high` (haute résolution) ou `low` (basse résolution)
- **Format**: `png` (recommandé, sans perte), `jpg` ou `webp`
- **Output Directory**: Dossier de destination (par défaut: `images`)

**Fonctionnement:**
1. Sélectionnez un set dans la liste déroulante
2. OU saisissez manuellement un nom/ID de set
3. Choisissez la langue, qualité, et format
4. Cliquez sur "⬇️ START DOWNLOAD"
5. Les images sont téléchargées dans `{output_dir}/{set_id}/`
6. Un fichier `manifest.csv` est généré avec les détails

**Sets Populaires Disponibles:**
- Surging Sparks (sv08)
- Stellar Crown (sv07)
- Shrouded Fable (sv06.5)
- Twilight Masquerade (sv06)
- Temporal Forces (sv05)
- Paldean Fates (sv04.5)
- Paradox Rift (sv04)
- Obsidian Flames (sv03)
- Paldea Evolved (sv02)
- Scarlet & Violet (sv01)
- Et plus de 10 autres sets classiques...

**Configuration Settings:**
Dans **⚙️ Settings → Image Download**:
- Default Output Directory
- Default Language
- Default Quality (high/low)
- Default Format (png/jpg/webp)
- Default Parallel Workers (1-16, recommandé: 4-8)

### 🔧 Via CLI (ligne de commande)

**Script:** `core/image_downloader.py`

**Usage basique:**
```powershell
python core/image_downloader.py --set "Surging Sparks"
```

**Options complètes:**
```powershell
python core/image_downloader.py `
  --set "sv08" `
  --output "images" `
  --lang "en" `
  --quality "high" `
  --ext "png" `
  --workers 8
```

**Paramètres:**
- `--set` : Nom ou ID du set (obligatoire)
  - Exemples: "Surging Sparks", "sv08", "base1", "Stellar Crown"
- `--output` : Dossier de sortie (défaut: `images`)
- `--lang` : Code langue (défaut: `en`)
  - Codes disponibles: `en`, `fr`, `de`, `it`, `es`, `pt`, `ja`, `ko`, `zh`, `th`
- `--quality` : Qualité (`high` ou `low`, défaut: `high`)
- `--ext` : Extension (`png`, `jpg` ou `webp`, défaut: `png`)
- `--workers` : Nombre de téléchargements parallèles (défaut: 8)

**Exemples:**

```powershell
# Télécharger Surging Sparks en français, PNG haute qualité
python core/image_downloader.py --set "Surging Sparks" --lang "fr" --quality "high" --ext "png"

# Télécharger Stellar Crown en anglais, JPG basse qualité (rapide)
python core/image_downloader.py --set "sv07" --lang "en" --quality "low" --ext "jpg"

# Télécharger Base Set 1 en allemand avec 12 workers
python core/image_downloader.py --set "base1" --lang "de" --workers 12
```

**Output:**
- Les images sont nommées avec leur numéro de set: `001.png`, `002.png`, etc.
- Un fichier `manifest.csv` est créé avec:
  - `filename`: Nom du fichier
  - `card_id`: ID TCGdex
  - `card_name`: Nom de la carte
  - `set_number`: Numéro dans le set
  - `url`: URL source TCGdex

**Notes importantes:**
- ✅ API gratuite, pas d'authentification requise
- ✅ Respect automatique des rate limits
- ✅ Retry automatique en cas d'erreur réseau
- ✅ Téléchargement parallèle pour vitesse optimale
- ⚠️ Utilise l'API TCGdex: https://api.tcgdex.net/v2

---

## 🎨 1. AUGMENTATION D'IMAGES

### Script : `augmentation.py`

Génère des images augmentées à partir des cartes originales avec diverses transformations.

### Utilisation via GUI
```batch
.\run_with_env.bat GUI.py
```
→ Onglet **"Augmentation de Dataset"**

### Utilisation en ligne de commande
```batch
.\run_with_env.bat augmentation.py [OPTIONS]
```

### Options disponibles

| Option | Valeur | Description |
|--------|--------|-------------|
| `--num_aug` | Nombre (défaut: 15) | Nombre d'augmentations par image |
| `--target` | `augmented` ou `images_aug` | Dossier de sortie |

### Exemples
```batch
# Générer 15 augmentations (défaut)
.\run_with_env.bat augmentation.py

# Générer 2 augmentations (test rapide)
.\run_with_env.bat augmentation.py --num_aug 2

# Spécifier le dossier de sortie
.\run_with_env.bat augmentation.py --target augmented
```

### Transformations appliquées
- **Flou** : Gaussian, Average, Median
- **Bruit** : Gaussian, Salt & Pepper
- **Distorsions** : Elastic, Piecewise Affine
- **Rotations** : -30° à +30°
- **Perspective** : Transformations 3D
- **Luminosité/Contraste**
- **Saturation/Teinte**

### Sortie
- **Dossier** : `output/augmented/`
- **Format** : YOLO (images + labels .txt)
- **Fichier** : `data.yaml` (configuration YOLO)

---

## 🌟 1.2. AUGMENTATION HOLOGRAPHIQUE

### Script : `holographic_augmenter.py`

**🆕 NOUVEAUTÉ GUI v3.0** : Génère des effets holographiques réalistes sur les cartes Pokémon pour simuler les finitions brillantes et irisées des vraies cartes.

### Utilisation via GUI
```batch
.\run_with_env.bat GUI_v3_modern.py
```
→ Vue **"Augmentation"** → Sélectionner type : **"Holographic"** ou **"Both"**

### Utilisation en ligne de commande
```batch
.\run_with_env.bat holographic_augmenter.py --input images --output images_holographic --intensity 0.7 --variations 3
```

### Options disponibles

| Option | Valeur | Description |
|--------|--------|-------------|
| `--input` | Dossier | Dossier source des images (défaut: `images`) |
| `--output` | Dossier | Dossier de sortie (défaut: `images_holographic`) |
| `--intensity` | 0.1-1.0 (défaut: 0.7) | Intensité de l'effet holographique |
| `--variations` | 1-10 (défaut: 3) | Nombre de variations par image |

### Exemples
```batch
# Effet standard (intensité 0.7, 3 variations)
.\run_with_env.bat holographic_augmenter.py --input images --output images_holographic

# Effet léger (intensité 0.3, 5 variations)
.\run_with_env.bat holographic_augmenter.py --intensity 0.3 --variations 5

# Effet intense (intensité 1.0, 10 variations)
.\run_with_env.bat holographic_augmenter.py --intensity 1.0 --variations 10
```

### Effets appliqués
- **Gradient arc-en-ciel** : Simulation du reflet holographique
- **Variations d'angle** : Différentes orientations de lumière
- **Intensité variable** : Contrôle de la force de l'effet
- **Préservation qualité** : Sans perte de détails de la carte

### Configuration dans Settings
Dans le **Settings Dialog** → Onglet **"Augmentation"** :
- **Holographic Intensity** : Curseur 0.1 à 1.0
- **Holographic Variations** : Spinbox 1 à 10

### Sortie
- **Dossier** : `images_holographic/` (ou dossier spécifié)
- **Format** : Images PNG avec effet holographique appliqué
- **Nomenclature** : `original_name_holo_X.png` (X = numéro variation)

---

## 🧩 2. GÉNÉRATION DE MOSAÏQUES

### Script : `mosaic.py`

Crée des mosaïques de 8 cartes sur des fonds variés avec différents layouts et transformations.

**🆕 NOUVEAUTÉ** : Fusion automatique des classes - si plusieurs cartes ont le même nom (variantes, éditions), elles sont traitées comme une seule classe pour YOLO.

### Utilisation via GUI
```batch
.\run_with_env.bat GUI_v3_modern.py
```
→ Vue **"Mosaic Generation"**

### Utilisation en ligne de commande
```batch
.\run_with_env.bat mosaic.py <layout_mode> <background_mode> <transform_mode> [max_groups]
```

**🆕 Nouveau paramètre optionnel** : `max_groups` - Limite le nombre de groupes à générer (1 groupe = 8 cartes)

### Modes de génération

**🆕 GUI v3.0** propose 3 modes prédéfinis :

| Mode | Groupes | Mosaïques | Description |
|------|---------|-----------|-------------|
| **Quick** | 25 | ~200 | Génération rapide pour tests |
| **Standard** | 62 | ~500 | Génération équilibrée (recommandé) |
| **Complete** | Tous | ~900 | Toutes les combinaisons (3×3×2×50) |

### Exemples de génération
```batch
# Génération standard (mode recommandé)
.\run_with_env.bat mosaic.py 1 0 0

# Quick test (limite à 25 groupes = 200 mosaïques)
.\run_with_env.bat mosaic.py 1 0 0 25

# Standard (limite à 62 groupes = 500 mosaïques)
.\run_with_env.bat mosaic.py 2 0 1 62

# Mode ALL via GUI (toutes les combinaisons)
.\run_with_env.bat mosaic.py ALL
```

### Paramètres

#### 🎯 Layout Mode (Position des cartes)

| Mode | Description | Caractéristiques |
|------|-------------|------------------|
| **1** | Grille avec rotation légère | • Grille 4×2<br>• Rotation ±10-20°<br>• Espacement régulier |
| **2** | Grille avec rotation forte | • Grille 4×2<br>• Rotation jusqu'à ±180°<br>• Peut inclure des flips horizontaux |
| **3** | Position aléatoire | • Positions complètement aléatoires<br>• Rotations aléatoires<br>• Peut créer des chevauchements |

#### 🖼️ Background Mode (Type de fond)

| Mode | Description | Source |
|------|-------------|---------|
| **0** | Mosaïque de fausses cartes | Images du dossier `fakeimg/` arrangées en grille |
| **1** | Image locale | Images du dossier `mosaic/` (si disponible) |
| **2** | Image du web | Téléchargement depuis Lorem Picsum (1920×1080) |

#### 🔄 Transform Mode (Type de transformation)

| Mode | Description | Effet |
|------|-------------|-------|
| **0** | Rotation 2D classique | Rotation simple autour du centre |
| **1** | Projection perspective 3D | Simulation d'inclinaison 3D (angles theta/phi) |

### Exemples

```batch
# Grille régulière + fond mosaïque + rotation 2D
.\run_with_env.bat mosaic.py 1 0 0

# Grille forte rotation + fond mosaïque + 3D
.\run_with_env.bat mosaic.py 2 0 1

# Position aléatoire + fond web + rotation 2D
.\run_with_env.bat mosaic.py 3 2 0

# Mode ALL (génère toutes les combinaisons)
.\run_with_env.bat mosaic.py ALL 0 0
```

### Sortie
- **Dossier** : `output/yolov8/`
- **Format** : YOLO (images + labels .txt)
- **Fichiers** :
  - `data.yaml` : Configuration YOLO
  - `annotations.json` : Annotations détaillées avec métadonnées

---

## 🖼️ 3. GÉNÉRATION DE FAUSSES CARTES (FAKE BACKGROUNDS)

### 🆕 Méthode recommandée : GUI v3.0

**🆕 NOUVEAUTÉ** : Vue dédiée avec configuration avancée dans le GUI v3.0

### Script moderne : `generate_fake_backgrounds.py`

Génère des fonds synthétiques avec bruit Perlin pour simuler des surfaces réalistes.

### Utilisation via GUI
```batch
.\run_with_env.bat GUI_v3_modern.py
```
→ Vue **"Fake Background Generator"** ou bouton dans vue **"Mosaic Generation"**

### Utilisation en ligne de commande
```batch
.\run_with_env.bat tools\generate_fake_backgrounds.py --count 100 --noise_min 10 --noise_max 50
```

### Options disponibles

| Option | Valeur | Description |
|--------|--------|-------------|
| `--count` | 10-1000 (défaut: 100) | Nombre de backgrounds à générer |
| `--noise_min` | 0-100 (défaut: 10) | Intensité minimale du bruit |
| `--noise_max` | 0-100 (défaut: 50) | Intensité maximale du bruit |

### Configuration dans Settings
Dans le **Settings Dialog** → Onglet **"Fake Backgrounds"** :
- **Default Count** : 10-1000 (défaut: 100)
- **Noise Min** : 0-100 (défaut: 10)
- **Noise Max** : 0-100 (défaut: 50)

### Exemples
```batch
# Génération standard (100 backgrounds)
.\run_with_env.bat tools\generate_fake_backgrounds.py

# Génération rapide (20 backgrounds)
.\run_with_env.bat tools\generate_fake_backgrounds.py --count 20

# Bruit intense (pour plus de variation)
.\run_with_env.bat tools\generate_fake_backgrounds.py --count 50 --noise_min 30 --noise_max 80
```

### Sortie
- **Dossier** : `fakeimg/`
- **Format** : PNG avec bruit Perlin
- **Utilisation** : Backgrounds pour mosaïques (background_mode=0)

---

### 🎲 Fake Backgrounds (Nouvelle Interface)

**Via GUI v3.0:**
1. Cliquer sur "🎲 Fake Backgrounds" dans la sidebar
2. Configurer:
   - **Nombre d'images** (défaut: 100)
   - **Output directory** (défaut: `fakeimg`)
   - **Min noise** (défaut: 20) - Valeurs basses = textures subtiles
   - **Max noise** (défaut: 60) - Valeurs hautes = motifs variés
3. Cliquer "🎲 GENERATE FAKE BACKGROUNDS"
4. Vérifier les logs et le dossier de sortie

**Via CLI:**
```bash
python tools/generate_fake_backgrounds.py --count 100 --output fakeimg --min-noise 20 --max-noise 60
```

**Paramètres disponibles:**
- `--count` : Nombre d'images à générer (défaut: 100)
- `--output` : Répertoire de sortie (défaut: `fakeimg`)
- `--min-noise` : Intensité minimale du bruit (0-100, défaut: 20)
- `--max-noise` : Intensité maximale du bruit (0-100, défaut: 60)

**💡 Tips:**
- Générer 100-500 images pour petits datasets, 500-1000 pour plus grands
- Valeurs basses (20-40) : textures subtiles
- Valeurs hautes (60-80) : motifs plus variés
- Les fake backgrounds sont automatiquement utilisés lors de la génération de mosaïques

**⚠️ Ancienne méthode (obsolète):**
- ~~`randomerasing.py`~~ : Remplacé par `generate_fake_backgrounds.py`
- ~~`generate_fakeimages.bat`~~ : Remplacé par la vue GUI dédiée

---

## 🧪 Tests rapides

### Test d'augmentation
```batch
.\tools\test_augmentation.bat
```
Génère 5 augmentations pour vérifier que tout fonctionne.

### Test de mosaïque
```batch
.\test_mosaic.bat
```
Génère quelques mosaïques avec les paramètres par défaut.

---

## 🎮 Interface Graphique (GUI v3.0)

### 🆕 Version moderne avec design Catppuccin Mocha

### Lancement
```batch
.\run_with_env.bat GUI_v3_modern.py
```
ou
```batch
.\run_gui_v3.bat
```

### 10 Vues disponibles

#### 📊 Dashboard
- **Statistiques** : Compteurs d'images/augmentations/mosaïques
- **Quick Actions** : Raccourcis vers fonctions principales
- **System Info** : Python version, packages installés
- **Charts** : Graphiques de distribution (si matplotlib disponible)

#### 🎨 Augmentation
- **Nombre d'augmentations** : 1-100 (défaut: 15)
- **Type** : Standard / Holographic / Both
- **Output directory** : augmented, images_aug, output/augmented
- **Bouton** : START AUGMENTATION

#### 📋 Fake Backgrounds
- **Vue dédiée** pour génération de fonds synthétiques
- **Configuration** : Count (10-1000), Noise min/max (0-100)
- **Statistiques** : Nombre de backgrounds actuels
- **Bouton** : GENERATE FAKE BACKGROUNDS

#### 🧩 Mosaic Generation
- **Mode** : Quick (200), Standard (500), Complete (All)
- **Card Layout** : Grid, 3D Rotation, Random Placement
- **Background** : Fake Cards Mosaic, Local Image, Web Image
- **Rotation** : 2D Rotation, 3D Perspective Projection
- **Boutons** : GENERATE MOSAICS, Generate Fake Backgrounds

#### ✅ Validation
- **Dataset path** : Chemin du dataset YOLO
- **Validation complète** : Vérification annotations et images
- **Rapport HTML** : Génération automatique
- **Bouton** : VALIDATE DATASET

#### 🎓 Training
- **YOLOv8 intégré** : Entraînement depuis le GUI
- **Configuration** : Model, epochs, batch size, device
- **Logs temps réel** : Suivi de l'entraînement
- **Visualisation** : Affichage des résultats

#### 🔍 Detection
- **3 modes** : Webcam, Video, Image
- **Configuration** : Model, confidence threshold, camera ID
- **Real-time** : Détection en direct
- **Boutons** : START WEBCAM, Detect Video, Detect Image

#### 🌐 API Server
- **TCGdex API** : Intégration gratuite (pas d'auth)
- **Flask REST** : Serveur API local
- **Endpoints** : Search cards, prices, Excel export
- **Status** : Monitoring du serveur

#### 🔄 Workflow
- **Quick Pipeline** : Fake → Augment → Mosaic → Train
- **Full Pipeline** : Processus complet automatisé
- **Custom** : Configuration personnalisée
- **Sauvegarde** : Export/Import workflows

#### ⚙️ Settings
**6 onglets de configuration** :
- **General** : 6 chemins (images, output, augmented, mosaic, fakeimg, holographic)
- **Augmentation** : Count, type, holographic params (intensity, variations)
- **Mosaic** : Mode, layout, background, transform
- **Fake Backgrounds** : Count, noise min/max
- **Training** : Model, epochs, batch, device
- **Advanced** : TCGdex API key

### Menu Tools (🛠️)

7 actions de nettoyage disponibles :
1. **Clean Outputs** : Supprime output/augmented/ et output/yolov8/
2. **Clean Fake Images** : Vide fakeimg/ et fakeimg_augmented/
3. **Clean Holographic** : Supprime images_holographic/
4. **Clean Web Backgrounds** : Vide web/
5. **Clean Training Results** : Supprime runs/train/
6. **Clean All Generated** : Tout sauf images sources
7. **Clean Everything** : Reset complet (confirmation double)

### Fonctionnalités supplémentaires
- **Logs temps réel** : Colorés avec émojis
- **Bouton Stop** : Annulation des opérations en cours
- **Auto-save config** : Sauvegarde automatique dans `gui_config.json`
- **Help button** : Lien direct vers le repository GitHub
- **Notifications** : Messages de succès/erreur

**📘 Documentation complète** : Voir `docs/GUI_V3_GUIDE.md`

---

## 🔧 Scripts utilitaires

### `install_env.bat`
Installe l'environnement virtuel et les dépendances.

### `run_with_env.bat`
Lance un script Python avec l'environnement activé.
```batch
.\run_with_env.bat <script.py> [arguments]
```

### `tools/test_augmentation.bat`
Test rapide de l'augmentation (5 augmentations par carte).

### `tools/test_mosaic.bat`
Test rapide des mosaïques.

### `fix_install.bat`
Répare une installation incomplète.

### `fix_numpy_conflict.bat`
Résout les conflits de version NumPy (NumPy 2.x vs 1.x).

---

## ⚠️ Dépannage

### Erreur : "No module named 'cv2'"
→ Exécutez `.\install_env.bat`

### Erreur : "No valid images found"
→ Vérifiez que :
- `images/` contient des cartes Pokémon pour l'augmentation
- `output/augmented/images/` contient des images pour les mosaïques
- `fakeimg/` contient des fonds (sinon exécutez `generate_fake_backgrounds.py`)

### Erreur NumPy : "AttributeError: np.bool"
→ Exécutez `.\fix_numpy_conflict.bat`

### Erreur : "Microsoft Visual C++ 14.0 is required"
→ Utilisez Python 3.12 (pas 3.13) : `.\install_env.bat` détecte automatiquement

### Warnings FutureWarning (np.bool, np.object)
→ Ces warnings sont normaux et n'affectent pas le fonctionnement. Ils proviennent de la compatibilité avec imgaug.

---

## 📊 Format de sortie YOLO

### Structure data.yaml
```yaml
train: images
val: images
nc: <nombre_de_classes>
names:
  - Nom_Carte_001
  - Nom_Carte_002
  - ...
```

### Format des labels (.txt)
```
<class_id> <x_center> <y_center> <width> <height>
```
- Coordonnées normalisées (0.0 à 1.0)
- `class_id` : correspond à l'index dans `data.yaml`

---

## 📦 Dépendances principales

- **NumPy** < 2.0 (1.26.4 recommandé)
- **OpenCV** < 4.10.0
- **imgaug** >= 0.4.0
- **pandas** >= 2.0
- **Pillow** >= 10.0
- **requests**
- **scipy**
- **scikit-image**
- **imagecorruptions**
- **openpyxl** (pour lire cards_info.xlsx)

---

## 💡 Workflow recommandé

1. **Préparation**
   ```batch
   .\install_env.bat
   ```

2. **Générer des fonds** (première fois seulement)
   ```batch
   .\generate_fakeimages.bat
   ```

3. **Augmenter les images**
   ```batch
   .\run_with_env.bat augmentation.py --num_aug 15
   ```

## 💡 Workflow recommandé

### Avec GUI v3.0 (RECOMMANDÉ)
1. **Préparation**
   ```batch
   .\install_env.bat
   .\run_gui_v3.bat
   ```

2. **Pipeline automatique** (via vue Workflow)
   - **Quick Pipeline** : Fake → Augment → Mosaic → Train
   - **Full Pipeline** : Processus complet automatisé
   
3. **OU étape par étape**
   - Vue **Fake Backgrounds** → Générer 100 backgrounds
   - Vue **Augmentation** → Type "Both" (Standard + Holographic)
   - Vue **Mosaic** → Mode "Standard (500)"
   - Vue **Training** → Entraîner YOLOv8

### En ligne de commande (traditionnel)
1. **Préparation**
   ```batch
   .\install_env.bat
   ```

2. **Générer des fonds** (première fois seulement)
   ```batch
   .\run_with_env.bat tools\generate_fake_backgrounds.py --count 100
   ```

3. **Augmenter les images**
   ```batch
   # Standard
   .\run_with_env.bat augmentation.py --num_aug 15
   
   # Holographic
   .\run_with_env.bat holographic_augmenter.py --intensity 0.7 --variations 3
   ```

4. **Générer des mosaïques**
   ```batch
   # Standard (500 mosaïques)
   .\run_with_env.bat mosaic.py 1 0 0 62
   .\run_with_env.bat mosaic.py 2 0 1 62
   
   # Quick test (200 mosaïques)
   .\run_with_env.bat mosaic.py 1 0 0 25
   ```

5. **Vérifier les résultats**
   - Images augmentées : `output/augmented/images/`
   - Images holographic : `images_holographic/`
   - Mosaïques : `output/yolov8/images/`
   - Configurations YOLO : `*.yaml`

---

## 📞 Support

Pour toute question, consultez :
- **`docs/GUI_V3_GUIDE.md`** : Documentation complète du GUI v3.0
- **`VERIFICATION_GUIDE.md`** : Vérification conformité guide ↔ code
- **`README.md`** : Vue d'ensemble du projet
- **`HELP.md`** : FAQ et dépannage
- Scripts de test : `test_augmentation.bat`, `test_mosaic.bat`

---

## 📝 Changelog

### Version 3.0 (Novembre 2025)
- 🆕 GUI v3.0 moderne avec design Catppuccin Mocha
- 🆕 Augmentation holographique (intensity, variations)
- 🆕 Modes Quick/Standard/Complete pour mosaïques
- 🆕 Générateur fake backgrounds avancé avec bruit Perlin
- 🆕 Dashboard avec statistiques et graphiques
- 🆕 Menu Clean Tools (7 actions)
- 🆕 Settings Dialog (6 onglets)
- 🆕 Workflow Manager (pipelines automatisés)
- 🆕 10 vues spécialisées
- ✅ Correction labels mosaic (Background 0=Fake, 1=Local, 2=Web)
- ✅ Limitation groupes via paramètre max_groups

### Version 1.0 (Octobre 2025)
- ✅ Augmentation standard avec imgaug
- ✅ Génération mosaïques YOLO
- ✅ Interface GUI basique
- ✅ Scripts CLI

---

**Version actuelle** : 3.0  
**Dernière mise à jour** : 2 novembre 2025  
**Auteur** : lo26lo  
**License** : MIT
