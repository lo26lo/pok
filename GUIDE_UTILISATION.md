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

## 🧩 2. GÉNÉRATION DE MOSAÏQUES

### Script : `mosaic.py`

Crée des mosaïques de 8 cartes sur des fonds variés avec différents layouts et transformations.

**🆕 NOUVEAUTÉ** : Fusion automatique des classes - si plusieurs cartes ont le même nom (variantes, éditions), elles sont traitées comme une seule classe pour YOLO.

### Utilisation via GUI
```batch
.\run_with_env.bat GUI.py
```
→ Onglet **"Génération de Mosaïques"**

### Utilisation en ligne de commande
```batch
.\run_with_env.bat mosaic.py <layout_mode> <background_mode> <transform_mode>
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

## 🖼️ 3. GÉNÉRATION DE FAUSSES CARTES

### Script : `randomerasing.py` + `generate_fakeimages.bat`

Crée des fausses cartes Pokémon en copiant 20 cartes aléatoires depuis `images/` vers `fakeimg/`, puis applique Random Erasing pour les modifier.

### Utilisation via batch (RECOMMANDÉ)
```batch
.\generate_fakeimages.bat
```

**Processus automatique** :
1. Nettoie le répertoire `fakeimg/`
2. Copie 20 cartes aléatoires depuis `images/`
3. Applique Random Erasing (probabilité 80%, effacement jusqu'à 50%)
4. Sauvegarde les versions modifiées dans `fakeimg_augmented/`

**Important** : `mosaic.py` utilise les images de `fakeimg/` (pas `fakeimg_augmented/`)

### Utilisation directe de randomerasing.py
```batch
.\run_with_env.bat randomerasing.py --input_dir fakeimg --output_dir fakeimg_augmented --p 0.8
```

### Fonds générés
20 cartes Pokémon aléatoires copiées depuis `images/`, avec Random Erasing appliqué pour créer des variations visuelles (zones effacées aléatoirement remplies de bruit).

---

## 🧪 Tests rapides

### Test d'augmentation
```batch
.\test_augmentation.bat
```
Génère 2 augmentations pour vérifier que tout fonctionne.

### Test de mosaïque
```batch
.\test_mosaic.bat
```
Génère quelques mosaïques avec les paramètres par défaut.

---

## 🎮 Interface Graphique (GUI)

### Lancement
```batch
.\run_with_env.bat GUI.py
```

### Onglets disponibles

#### 📊 Onglet 1 : Augmentation de Dataset
- **Nombre d'augmentations** : Combien de variations par image
- **Cible** : Dossier de sortie (`augmented` ou `images_aug`)
- **Bouton** : Lancer Augmentation

#### 🧩 Onglet 2 : Génération de Mosaïques
- **Layout Mode** : Type de disposition (1, 2 ou 3)
- **Background Mode** : Type de fond (0, 1 ou 2)
- **Transform Mode** : Type de transformation (0 ou 1)
- **Bouton** : Lancer Mosaïque

#### 🛠️ Onglet 3 : Outils
- Options supplémentaires (si disponibles)

#### 📝 Onglet 4 : Logs
- Affichage des logs d'exécution

---

## 🔧 Scripts utilitaires

### `install_env.bat`
Installe l'environnement virtuel et les dépendances.

### `run_with_env.bat`
Lance un script Python avec l'environnement activé.
```batch
.\run_with_env.bat <script.py> [arguments]
```

### `generate_fakeimages.bat`
Génère automatiquement 10 images de fond dans `fakeimg/`.

### `test_augmentation.bat`
Test rapide de l'augmentation (2 augmentations).

### `test_mosaic.bat`
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

4. **Générer des mosaïques**
   ```batch
   .\run_with_env.bat mosaic.py 1 0 0
   .\run_with_env.bat mosaic.py 2 0 1
   .\run_with_env.bat mosaic.py 3 2 0
   ```

5. **Vérifier les résultats**
   - Images augmentées : `output/augmented/images/`
   - Mosaïques : `output/yolov8/images/`
   - Configurations YOLO : `*.yaml`

---

## 📞 Support

Pour toute question, consultez :
- `STRUCTURE_RECOMMANDEE.md` pour l'architecture du projet
- Les scripts de test : `test_augmentation.bat`, `test_mosaic.bat`

---

**Version** : 1.0  
**Dernière mise à jour** : 29 octobre 2025
