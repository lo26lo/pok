# 🛠️ Outils et Utilitaires

Ce dossier contient les scripts utilitaires et outils de développement du projet Pokemon Dataset Generator.

## 📝 Scripts Utilitaires

### Création d'Exemples
- **`create_annotated_example.py`** - Crée des exemples avec bounding boxes YOLO
- **`create_annotation_text_image.py`** - Visualise les fichiers d'annotations .txt
- **`create_banner.py`** - Génère la bannière du README

### Création d'Executable
- **`create_exe.py`** - Script Python pour créer l'executable Windows
- **`create_exe.bat`** - Wrapper batch pour `create_exe.py`

### Tests
- **`test_augmentation.bat`** - Test rapide de l'augmentation
- **`test_augmentation_variety.py`** - Test de la variété des augmentations
- **`test_augmentation_variety.bat`** - Wrapper pour le test de variété
- **`test_mosaic.bat`** - Test rapide des mosaïques

### Utilitaires
- **`check_excel.py`** - Vérifie l'intégrité du fichier Excel
- **`generate_fake_backgrounds.py`** - Génère des fonds d'images factices
- **`pokemon_utils.py`** - Fonctions utilitaires Pokemon
- **`randomerasing.py`** - Algorithme Random Erasing

### Corrections
- **`fix_install.bat`** - Corrige les problèmes d'installation
- **`fix_numpy_conflict.bat`** - Résout les conflits NumPy
- **`numpy_imgaug_patch.py`** - Patch pour compatibilité NumPy/imgaug

## 📂 Usage depuis la Racine

Tous ces scripts sont conçus pour être exécutés **depuis la racine du projet** :

```batch
# Exemple
cd C:\Users\...\Pokemons
python tools\create_pikachu_icon.py
```

## ⚠️ Note

Ces scripts ne sont **pas utilisés directement par le GUI**. Ils sont destinés au développement, aux tests et à la maintenance du projet.
