# 🎮 Pokemon Dataset Generator

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9-green.svg)](https://opencv.org/)

Un outil complet pour générer des datasets d'images de cartes Pokémon augmentées avec annotations YOLO pour l'entraînement de modèles de détection d'objets.

## 🖼️ Exemples de Génération

<table>
<tr>
<td align="center">
<img src="examples/example_fakeimg.png" alt="Fake Background" width="250"/>
<br/>
<strong>Fake Background</strong>
<br/>
<em>Carte avec Random Erasing</em>
</td>
<td align="center">
<img src="examples/example_augmented.png" alt="Augmented Card" width="250"/>
<br/>
<strong>Augmented Card</strong>
<br/>
<em>Augmentation avec imgaug</em>
</td>
<td align="center">
<img src="examples/example_layout.png" alt="YOLO Layout" width="250"/>
<br/>
<strong>YOLO Layout</strong>
<br/>
<em>Mosaïque 8 cartes annotées</em>
</td>
</tr>
</table>

![Pokemon Dataset Generator Banner](https://via.placeholder.com/800x200/0078D4/FFFFFF?text=Pokemon+Dataset+Generator+v2.0)

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [GUI v2.0](#-gui-v20)
- [Workflow](#-workflow)
- [Configuration](#-configuration)
- [Documentation](#-documentation)
- [Contribution](#-contribution)
- [Licence](#-licence)

## ✨ Fonctionnalités

### 🎨 Augmentation d'Images
- **Augmentations multiples** par image avec imgaug
- Support des formats **PNG avec canal alpha** (RGBA → RGB)
- Génération automatique d'annotations **YOLO**
- Effets variés : flou, contraste, saturation, fog, posterize, sharpen, emboss

### 🧩 Génération de Mosaïques
- **3 modes de layout** : Grille, Rotation forte, Aléatoire
- **3 modes de background** : Mosaïque, Local, Web
- **2 modes de transformation** : Rotation 2D, Perspective 3D
- **Fusion de classes** pour variantes de cartes
- Annotations YOLO avec polygones à 4 points

### 🖼️ Fausses Cartes (Random Erasing)
- Génération de cartes avec zones effacées
- Probabilité d'effacement configurable (0.0 - 1.0)
- Utilisées comme fond de mosaïque

### 🖥️ Interface Graphique Moderne (GUI v2.0)
- **Dashboard** avec statistiques en temps réel
- **Validation automatique** des prérequis
- **Barre de progression** avec annulation
- **Multi-threading** (interface non-bloquante)
- **Configuration persistante** (gui_config.json)
- **Workflow complet automatique**

### 🔧 Utilitaires API Pokémon TCG (Nouveau!)
- **Génération automatique** de listes de cartes par extension
- **Mise à jour des prix** TCGPlayer depuis l'API
- **Recherche rapide** d'une carte avec affichage des prix
- **Clé API incluse** - prêt à l'emploi
- **Traitement parallélisé** pour performances optimales

## 🚀 Installation

### Prérequis
- **Python 3.12** (recommandé pour les wheels pré-compilés)
- **Windows** (scripts batch fournis)
- **Git** (optionnel)

### Installation Automatique

```batch
# 1. Cloner le dépôt
git clone https://github.com/lo26lo/pok.git
cd pok/Pokemons

# 2. Installer l'environnement (Python 3.12 + dépendances)
install_env.bat
```

L'installateur va :
- ✅ Détecter ou installer Python 3.12
- ✅ Créer un environnement virtuel `.venv`
- ✅ Installer toutes les dépendances compatibles
- ✅ Configurer NumPy < 2.0 pour compatibilité imgaug

### Installation Manuelle

```batch
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## 📖 Utilisation

### Lancement du GUI v2.0 (Recommandé)

```batch
run_gui_v2_with_env.bat
```

### Utilisation en Ligne de Commande

#### Augmentation
```batch
# Activer l'environnement
.venv\Scripts\activate

# Générer 15 augmentations par image
python augmentation.py --num_aug 15 --target augmented
```

#### Mosaïques
```batch
# Layout=1 (Grille), Background=0 (Mosaïque), Transform=0 (2D)
python mosaic.py 1 0 0
```

#### Fausses Cartes
```batch
# Probabilité 0.8, sh=0.5
python randomerasing.py --input_dir fakeimg --output_dir fakeimg_augmented --p 0.8 --sh 0.5
```

## 📁 Structure du Projet

```
Pokemons/
├── 📱 GUI_v2.py                    # Interface graphique moderne
├── 🎨 augmentation.py              # Script d'augmentation
├── 🧩 mosaic.py                    # Génération de mosaïques
├── 🖼️ randomerasing.py             # Random Erasing
├── 🛠️ pokemon_utils.py             # Utilitaires
├── ⚙️ config.py                    # Configuration
│
├── 📦 requirements.txt             # Dépendances Python
├── 🔧 gui_config.json             # Configuration GUI (auto-généré)
├── 📊 cards_info.xlsx             # Informations des cartes
│
├── 🚀 Fichiers Batch
│   ├── install_env.bat            # Installation environnement
│   ├── run_gui_v2_with_env.bat    # Lancer GUI v2
│   ├── test_augmentation.bat      # Test rapide (5 aug)
│   └── generate_fakeimages.bat    # Générer fausses cartes
│
├── 📂 Dossiers de Données
│   ├── images/                    # 📥 Cartes sources (INPUT)
│   ├── fakeimg/                   # Fausses cartes temporaires (générées)
│   ├── fakeimg_augmented/         # Fausses cartes traitées (générées)
│   ├── examples/                  # 🖼️ Images d'exemple pour README
│   └── output/
│       ├── augmented/
│       │   ├── images/            # 📤 Images augmentées (OUTPUT - générées)
│       │   ├── labels/            # Annotations YOLO (générées)
│       │   └── data.yaml          # Config YOLO
│       └── yolov8/
│           ├── images/            # 📤 Mosaïques (OUTPUT - générées)
│           ├── labels/            # Annotations YOLO (générées)
│           └── data.yaml          # Config YOLO
│
└── 📚 Documentation
    ├── README.md                  # Ce fichier
    ├── README_GUI_V2.md          # Guide GUI v2.0
    ├── CHANGELOG_GUI_V2.md       # Changements v2.0
    ├── GUIDE_UTILISATION.md      # Guide complet
    └── RECAPITULATIF_FINAL.md    # Récapitulatif projet
```

## 🖥️ GUI v2.0

### Onglets

#### 📊 Dashboard
- Statistiques en temps réel
- Actions rapides (ouvrir dossiers, nettoyer)
- **Workflow complet automatique**

#### 🎨 Augmentation
- Validation automatique des images sources
- Presets : Rapide (5), Standard (15), Intensif (100)
- Configuration du nombre d'augmentations

#### 🧩 Mosaïques
- Configuration des 3 modes (layout, background, transform)
- Validation des images augmentées

#### 🖼️ Fausses Cartes
- Nombre de cartes : 10-50 (slider)
- Random Erasing : On/Off
- Probabilité : 0.0-1.0 (slider)

#### � Utilitaires
**Intégration complète de l'API Pokémon TCG :**

##### 📋 Générer Liste de Cartes
- Saisir nom de l'extension (ex: "Surging Sparks")
- Choisir nom du fichier Excel de sortie
- Génère automatiquement toutes les cartes avec `Set #` et `Name`

##### 💰 Mettre à Jour les Prix
- Charger un fichier Excel avec `Set #`, `Name`, `Set`
- Interroge l'API pour chaque carte (parallélisé)
- Ajoute colonnes `Prix` et `Prix max`
- Résumé des erreurs affiché à la fin

##### 🔍 Recherche Rapide
- Saisir nom de la carte (requis)
- Numéro et Set optionnels pour filtrer
- Affiche popup avec tous les prix disponibles

**💡 Clé API incluse** - Aucune configuration nécessaire!

#### �📝 Logs
- Horodatage automatique
- Copier / Sauvegarder / Effacer
- Export en fichier .log

### Menu Settings ⚙️

Personnalisation complète des chemins :
- 📁 Dossier Images Sources
- 🖼️ Dossier Fausses Cartes
- 📤 Sortie Augmentation
- 🧩 Sortie Mosaïques
- 📊 Fichier Excel

## 🔄 Workflow

### Option 1 : Workflow Automatique

1. Lancer le GUI : `run_gui_v2_with_env.bat`
2. Dashboard → **▶️ Démarrer Workflow**
3. Le système exécute automatiquement :
   - Génération de 20 fausses cartes (Random Erasing p=0.8)
   - Augmentation de toutes les images (15 par carte)
   - Génération des mosaïques YOLO

### Option 2 : Workflow Manuel

#### Étape 1 : Préparer les Données
```
1. Placer les images de cartes dans images/
2. Créer/vérifier cards_info.xlsx avec colonnes:
   - Set # (ex: 001/191)
   - Name (ex: Pikachu)
```

#### Étape 2 : Générer les Fausses Cartes
```batch
# GUI: Onglet 🖼️ Fausses Cartes
# - Nombre: 20
# - Random Erasing: ✅
# - Probabilité: 0.8
# - Cliquer "▶️ Générer"
```

#### Étape 3 : Augmentation
```batch
# GUI: Onglet 🎨 Augmentation
# - Preset: Standard (15)
# - Cible: augmented
# - Cliquer "▶️ Lancer"

# OU en ligne de commande:
python augmentation.py --num_aug 15 --target augmented
```

#### Étape 4 : Mosaïques
```batch
# GUI: Onglet 🧩 Mosaïques
# - Configurer les modes
# - Cliquer "▶️ Générer"

# OU en ligne de commande:
python mosaic.py 1 0 0
```

## ⚙️ Configuration

### Format des Noms de Fichiers

Le système supporte plusieurs formats :
- `SSP_001_R_EN_SM.png` ✅
- `pokemon_en_001_xyz.jpg` ✅
- `card_001.png` ✅

Le numéro à 3 chiffres doit correspondre au **Set #** dans `cards_info.xlsx`.

### Fichier Excel (cards_info.xlsx)

| Set #   | Name      |
|---------|-----------|
| 001/191 | Pikachu   |
| 002/191 | Raichu    |
| 003/191 | Mewtwo    |

### Configuration GUI (gui_config.json)

```json
{
    "paths": {
        "images_source": "images",
        "fakeimg": "fakeimg",
        "output_augmented": "output\\augmented",
        "output_mosaic": "output\\yolov8",
        "excel_file": "cards_info.xlsx"
    },
    "last_used": {
        "num_aug": 15,
        "target": "augmented",
        "layout_mode": 1,
        "background_mode": 0,
        "transform_mode": 0,
        "random_erasing_p": 0.2
    }
}
```

## 📊 Formats de Sortie

### Structure YOLO

```
output/yolov8/
├── images/
│   ├── layout_001.png
│   ├── layout_002.png
│   └── ...
├── labels/
│   ├── layout_001.txt
│   ├── layout_002.txt
│   └── ...
└── data.yaml
```

### Format des Annotations (.txt)

```
class_id center_x center_y width height
0 0.512345 0.345678 0.123456 0.234567
1 0.789012 0.456789 0.098765 0.187654
```

Coordonnées normalisées (0.0 - 1.0)

## 📚 Documentation

- **[README_GUI_V2.md](README_GUI_V2.md)** - Guide détaillé du GUI v2.0
- **[CHANGELOG_GUI_V2.md](CHANGELOG_GUI_V2.md)** - Liste des changements v2.0
- **[GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)** - Guide utilisateur complet
- **[RECAPITULATIF_FINAL.md](RECAPITULATIF_FINAL.md)** - Récapitulatif projet

## 🛠️ Dépendances

### Principales

- **Python 3.12** - Environnement d'exécution
- **NumPy < 2.0** - Calculs numériques (compatibilité imgaug)
- **OpenCV < 4.10.0** - Traitement d'images (compatibilité NumPy 1.x)
- **imgaug 0.4.0** - Augmentations d'images
- **pandas** - Lecture du fichier Excel
- **openpyxl** - Support Excel (.xlsx)
- **Pillow** - Manipulation d'images
- **scikit-image** - Traitement d'images avancé
- **scipy** - Calculs scientifiques

### Complètes

Voir [requirements.txt](requirements.txt)

## 🐛 Dépannage

### Erreur "ModuleNotFoundError: No module named 'cv2'"

```batch
# Réinstaller l'environnement
install_env.bat
```

### Erreur "No module named 'openpyxl'"

```batch
.venv\Scripts\activate
pip install openpyxl
```

### Images RGBA (4 canaux)

✅ **Géré automatiquement** - Conversion RGBA → RGB incluse

### "Aucune image valide trouvée"

Vérifier :
1. Les images sont dans `images/`
2. Le format des noms correspond au pattern (ex: `SSP_001_...`)
3. Les numéros correspondent à `cards_info.xlsx`

### Diagnostic Complet

Dans le GUI : **Menu Outils → Diagnostiquer Environnement**

## 📈 Résultats Typiques

Pour 257 cartes sources avec 15 augmentations :

```
📥 INPUT
├── 257 images sources (PNG)
└── 1 fichier Excel

⚙️ PROCESSING
├── 20 fausses cartes générées
├── 514 images augmentées (257 × 2)
└── ~65 mosaïques

📤 OUTPUT
├── 514 images augmentées + labels YOLO
└── 65 mosaïques + labels YOLO
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Changelog

### Version 2.0 (Octobre 2025)
- ✨ GUI modernisé avec Dashboard
- ✨ Menu Settings pour configuration des chemins
- ✨ Validation automatique des prérequis
- ✨ Barre de progression avec annulation
- ✨ Multi-threading (interface non-bloquante)
- ✨ Onglet Fausses Cartes intégré
- ✨ Workflow complet automatique
- ✨ Configuration persistante
- 🐛 Support format PNG RGBA
- 🐛 Détection améliorée des numéros de cartes
- 🐛 Fix ID mapping YOLO (ID = numéro de carte)
- ⚡ Optimisation mosaic.py (préchargement fake images)
- 📦 .gitignore optimisé (exclusion fichiers générés)

Voir [CHANGELOG_GUI_V2.md](CHANGELOG_GUI_V2.md) pour plus de détails.

---

## ⚠️ Note sur les Fichiers Générés

Les dossiers suivants contiennent des fichiers **générés automatiquement** et ne sont **pas versionnés sur GitHub** :
- `output/augmented/images/` et `output/augmented/labels/`
- `output/yolov8/images/` et `output/yolov8/labels/`
- `fakeimg/` et `fakeimg_augmented/`

Ces dossiers seront **créés automatiquement** lors de l'exécution des scripts. Les images d'exemple se trouvent dans le dossier `examples/`.

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👤 Auteur

**lo26lo**
- GitHub: [@lo26lo](https://github.com/lo26lo)
- Repository: [pok](https://github.com/lo26lo/pok)

## 🙏 Remerciements

- **imgaug** - Librairie d'augmentation d'images
- **OpenCV** - Traitement d'images
- **YOLOv8** - Format d'annotations
- **Ultralytics** - Documentation YOLO

## 📞 Support

Pour toute question ou problème :
1. Consulter la [documentation](GUIDE_UTILISATION.md)
2. Vérifier les [issues existantes](https://github.com/lo26lo/pok/issues)
3. Créer une [nouvelle issue](https://github.com/lo26lo/pok/issues/new)

---

⭐ **N'oubliez pas de mettre une étoile si ce projet vous a été utile !** ⭐

