# GUI v3.2 Professional - Guide Complet

## 🎨 Nouvelle Interface

L'interface v3.2 apporte une refonte complète avec :

- **Sidebar moderne** : Navigation hiérarchique claire
- **Design professionnel** : Palette Catppuccin Mocha
- **Champs optimisés** : Fond blanc + texte foncé pour meilleure lisibilité
- **9 vues fonctionnelles** : Toutes opérationnelles

## 📂 Structure Modulaire

```
pok/
├── GUI_v3_modern.py          # Interface v3.0
├── run_gui_v3.bat            # Lancement facile
│
└── core/                      # Modules métier séparés
    ├── workflow_manager.py    # Pipeline automatique
    ├── training_manager.py    # Entraînement YOLO
    ├── detection_manager.py   # Détection temps réel
    ├── augmentation.py        # Augmentation images
    ├── mosaic.py              # Mosaïques YOLO
    ├── dataset_validator.py   # Validation dataset
    ├── dataset_exporter.py    # Export multi-format
    ├── auto_balancer.py       # Équilibrage classes
    └── ...
```

## 🚀 Lancement

### Méthode 1 : Batch file (Recommandé)
```bash
run_gui_v3.bat
```

### Méthode 2 : Manuel
```bash
.venv\Scripts\activate
python GUI_v3_modern.py
```

## 📋 Fonctionnalités par Vue

### 🏠 Home (Dashboard)
- **Stats en temps réel** : Images, augmentations, mosaïques, détections
- **Quick actions** : Boutons rapides vers vues principales
- **Status système** : Vérification dataset, modèles, API

### 🚀 Auto Workflow
**Pipeline complet automatisé**
- Augmentation (5-100 variations/carte)
- Génération mosaïques (Quick/Standard/Complete)
- Validation dataset (optionnel)
- Auto-balancing classes (optionnel)
- Entraînement YOLO (optionnel)

**Configuration :**
```python
Augmentations: 15 (par défaut)
Mosaics: Standard (500)
✅ Validation activée
⚖️ Balancing désactivé
🎓 Training désactivé
```

**Durée estimée** : Affichée avant lancement

### 🎨 Augmentation
**Génération de variations augmentées**
- Nombre de variations : 1-100
- Dossier de sortie : configurable
- Techniques : Rotation, flip, blur, brightness, etc.

**Usage :**
1. Configurer nombre d'augmentations
2. Choisir dossier de sortie
3. Cliquer "START AUGMENTATION"

### 🧩 Mosaics
**Création de mosaïques YOLO**
- Quick (200) : Génération rapide
- Standard (500) : Équilibre vitesse/quantité
- Complete (All) : Toutes combinaisons possibles

**Usage :**
1. Sélectionner mode
2. Cliquer "GENERATE MOSAICS"
3. Attendre génération (logs temps réel)

### ✅ Validation
**Vérification qualité dataset**
- Détection annotations invalides
- Vérification images corrompues
- Statistiques par classe
- Génération rapport HTML

**Usage :**
1. Sélectionner dataset (output/yolov8 par défaut)
2. Cocher "Generate HTML report"
3. Cliquer "VALIDATE DATASET"
4. Consulter rapport via "Open Report"

### 🎓 Training
**Entraînement modèle YOLOv8**

**Configuration :**
- **Model** : yolov8n, s, m, l (nano à large)
- **Epochs** : 10-500 (50 par défaut)
- **Batch** : 4-64 (16 par défaut)
- **Device** : 0 (GPU), cpu, multi-GPU

**Usage :**
1. Configurer hyperparamètres
2. Cliquer "START TRAINING"
3. Suivre progression dans logs
4. Voir résultats via "View Results"

**Modèle sauvegardé :**
```
runs/train/pokemon_detector/weights/best.pt
```

### 📹 Detection
**Détection temps réel et batch**

**3 modes disponibles :**

#### 1. Webcam Live
- Détection temps réel
- Affichage FPS
- Appuyer 'q' pour quitter

#### 2. Image Unique
- Sélectionner 1 image
- Affichage résultat immédiat
- Bounding boxes + confiance

#### 3. Dossier Batch
- Traitement multiple images
- Sauvegarde résultats annotés
- Export dans `detections/`

**Configuration :**
- Model path : runs/train/pokemon_detector/weights/best.pt
- Confidence : 0.1-1.0 (0.25 par défaut)
- Camera ID : 0-10 (webcam)

### 📦 Export
**Export multi-format**

**Formats disponibles :**
- ✅ **COCO JSON** : Format standard, compatible avec de nombreux outils
- 🗂️ **Pascal VOC XML** : Format classique, compatible TensorFlow Object Detection
- 🤖 **TensorFlow TFRecord** : Format optimisé TensorFlow
- 📦 **Roboflow ZIP** : Format prêt pour upload Roboflow

**Usage :**
1. Cocher formats souhaités
2. Cliquer "EXPORT DATASET"
3. Attendre export (peut prendre du temps pour TFRecord)

**Exports sauvegardés dans :**
```
output/
├── coco/
├── voc/
├── tfrecord/
└── roboflow/
```

### 🛠️ Utilities
**Outils additionnels**

- **⚖️ Auto-Balance Classes** : Équilibre distribution classes
- **✨ Holographic Augmenter** : Effets holographiques sur cartes
- **🎴 TCG API Browser** : Parcourir API Pokemon TCG
- **📊 Statistics Dashboard** : Stats complètes dataset
- **🗂️ Open Output Folder** : Ouvrir dossier output

## 🎯 Workflow Recommandé

### Débutant (Quick Start)
```
1. Home → Vérifier stats
2. Auto Workflow → Config rapide → START
3. Attendre fin (~5-10 min)
4. Training → Entraîner modèle (~30 min)
5. Detection → Tester webcam
```

### Avancé (Contrôle Total)
```
1. Augmentation → 20 variations
2. Mosaic → Complete mode
3. Validation → Vérifier qualité
4. Utilities → Auto-balance
5. Export → Formats multiples
6. Training → 100 epochs
7. Detection → Batch processing
```

## ⚙️ Configuration

### Fichiers de config
- `gui_config.json` : Paramètres GUI sauvegardés
- `api_config.json` : Clé API Pokemon TCG
- `models/cards_database.yaml` : Base de données cartes (YAML)

### Dossiers importants
```
images/           # Images sources
output/
  ├── augmented/  # Images augmentées
  └── yolov8/     # Dataset YOLO formaté
runs/
  └── train/      # Modèles entraînés
```

## 🐛 Dépannage

### Erreur "NumPy 2.0"
**Solution :** Utiliser environnement virtuel
```bash
.venv\Scripts\activate
python -c "import numpy; print(numpy.__version__)"
# Doit afficher: 1.26.x
```

### Erreur "ultralytics not found"
**Solution :** Installer dépendances extras
```bash
pip install -r requirements_extra.txt
```

### Webcam ne démarre pas
**Causes :**
- OpenCV pas installé
- Webcam utilisée par autre app
- Mauvais Camera ID

**Solutions :**
```bash
pip install opencv-python
# Essayer Camera ID : 0, 1, 2
```

### Modèle non trouvé
**Solution :** Vérifier chemin
```
runs/train/pokemon_detector/weights/best.pt
```
Si absent → Entraîner un modèle d'abord

## 📚 Ressources

### Documentation
- `core/README.md` : Documentation modules core
- `docs/` : Documentation détaillée projet
- `NOUVELLES_FONCTIONNALITES.md` : Changelog complet

### Exemples
- `examples/` : Exemples de code
- `tools/` : Scripts utilitaires

## 🆕 Nouveautés v3.0

### Interface
- ✅ Sidebar moderne avec navigation hiérarchique
- ✅ Palette de couleurs professionnelle
- ✅ Champs de saisie optimisés (fond blanc + texte foncé)
- ✅ Toutes les vues fonctionnelles (plus de placeholders)
- ✅ Progress bars et feedback temps réel

### Architecture
- ✅ Séparation GUI / Logique métier
- ✅ 3 nouveaux managers (Workflow, Training, Detection)
- ✅ Annotations complètes (type hints)
- ✅ Callbacks pour communication GUI ↔ Core
- ✅ Threading pour opérations longues

### Fonctionnalités
- ✅ Pipeline automatique complet
- ✅ Entraînement YOLO intégré
- ✅ Détection temps réel webcam
- ✅ Export multi-format
- ✅ Validation dataset améliorée
- ✅ Auto-balancing classes

## 🎨 Personnalisation

### Changer les couleurs
Éditer `GUI_v3_modern.py`, ligne ~50 :
```python
self.colors = {
    'bg_dark': '#1e1e2e',    # Background
    'accent': '#89b4fa',     # Accent blue
    'success': '#a6e3a1',    # Green
    # ...
}
```

### Ajouter une vue
1. Créer méthode `create_myview_view()`
2. Ajouter dans `create_sidebar()` :
```python
self.create_nav_item("🆕 My View", "myview", "MY_SECTION")
```
3. Ajouter dans `show_view()` :
```python
elif view_name == 'myview':
    self.create_myview_view()
```

## 📞 Support

En cas de problème :
1. Vérifier logs dans GUI (section en bas)
2. Consulter `validation_report.html` si erreurs dataset
3. Vérifier environnement virtuel actif
4. Relancer avec `run_gui_v3.bat`

---

**Version** : 3.0.0  
**Date** : Octobre 2025  
**Auteur** : Pokemon Dataset Generator Team
