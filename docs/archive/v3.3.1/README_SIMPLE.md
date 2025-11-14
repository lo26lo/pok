# 🎮 Pokémon Dataset Generator v3.2

**Pipeline complet YOLO : Génération de dataset → Entraînement → Détection avec prix**

---

## 🚀 Démarrage Rapide

### 1️⃣ Installation (première fois)
```batch
INSTALL.bat
```

### 2️⃣ Lancement de l'application
```batch
START.bat
```

C'est tout ! L'interface graphique moderne s'ouvre automatiquement.

---

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| **[docs/README.md](docs/README.md)** | Documentation complète du projet |
| **[docs/README_SCRIPTS_SYSTEM.md](docs/README_SCRIPTS_SYSTEM.md)** | Système de gestion des scripts |
| **[docs/DEPENDENCIES_MAP.md](docs/DEPENDENCIES_MAP.md)** | Cartographie des dépendances |
| **[docs/DEPENDENCY_GRAPH.md](docs/DEPENDENCY_GRAPH.md)** | Diagrammes interactifs |
| **[docs/HELP.md](docs/HELP.md)** | Guide d'utilisation |
| **[docs/CHANGELOG.md](docs/CHANGELOG.md)** | Historique des versions |

---

## 📁 Structure du Projet

```
pok/
├── START.bat              ← Lance l'application GUI
├── INSTALL.bat            ← Installe l'environnement Python
├── README.md              ← Ce fichier
│
├── core/                  ← Modules principaux
├── scripts/               ← Scripts et utilitaires
├── tests/                 ← Tests automatisés
├── docs/                  ← Documentation complète
├── config/                ← Fichiers de configuration
├── models/                ← Modèles YOLO et mappings
│
├── images/                ← Images téléchargées
├── augmented/             ← Images augmentées
├── output/                ← Datasets générés
├── runs/                  ← Résultats d'entraînement
└── excel/                 ← Fichiers Excel de prix
```

---

## ✨ Fonctionnalités Principales

### 🎨 Interface GUI Moderne
- Dashboard avec statistiques en temps réel
- 9 onglets fonctionnels organisés
- Vérification automatique de l'environnement
- Mode sombre / clair

### 📥 Téléchargement d'Images
- API TCGdex intégrée
- Support multi-langues (EN, FR, ES, DE, IT, PT, etc.)
- Téléchargement par set ou global
- Barre de progression en temps réel

### 🎨 Augmentation Intelligente
- **22 types d'augmentation** : rotation, flip, bruit, flou, contraste, HSV, perspective...
- **Effets holographiques** : 5 styles (rainbow, linear, radial, metallic, glitter)
- **Auto-balancer** : Équilibre automatique du dataset
- **Mosaïques annotées** : Génération avec bounding boxes

### 🎯 Entraînement YOLO
- YOLOv8 / YOLOv11 supportés
- GPU CUDA automatique
- Paramètres personnalisables
- Export multi-formats (YOLO, VOC, COCO, CSV)

### 🔍 Détection avec Prix
- Détection webcam en temps réel
- Affichage des prix (TCGdex API)
- Mapping automatique carte → ID
- Statistiques de confiance

### 🔄 Workflow Complet
- Pipeline automatisé de bout en bout
- Configuration sauvegardée (JSON)
- Logs détaillés
- Reprise sur erreur

---

## 🛠️ Scripts Utilitaires

### Depuis la racine :
```batch
# Lancer l'application
START.bat

# Installer/Réinstaller l'environnement
INSTALL.bat
```

### Depuis scripts/ :
```batch
# Exécuter tous les tests
scripts\run_all_tests.bat

# Exécuter un script spécifique
scripts\run_script.bat <nom_script>

# Exécuter un test spécifique
scripts\run_test.bat <nom_test>
```

**Voir [docs/README_SCRIPTS_SYSTEM.md](docs/README_SCRIPTS_SYSTEM.md) pour la liste complète**

---

## 🧪 Tests

```batch
# Tous les tests
scripts\run_all_tests.bat

# Tests par catégorie
scripts\run_all_tests.bat Integration
scripts\run_all_tests.bat Performance
scripts\run_all_tests.bat Validation

# Test GPU CUDA
scripts\test_pytorch_gpu.bat
```

---

## 📦 Configuration

Les fichiers de configuration sont dans `config/` :

- **requirements.txt** : Dépendances Python principales
- **requirements_training.txt** : Dépendances pour l'entraînement
- **requirements_extra.txt** : Dépendances optionnelles
- **api_config.json.example** : Configuration API TCGdex
- **gui_config.json** : Configuration de l'interface

---

## 🎯 Workflow Typique

1. **Télécharger les images** (onglet Image Download)
2. **Initialiser les prix** : `scripts\run_script.bat init_prices`
3. **Augmenter les images** (onglet Augmentation)
4. **Générer le dataset** (onglet Full Workflow)
5. **Entraîner YOLO** (onglet Training)
6. **Tester la détection** (onglet Detection)

---

## 🔧 Maintenance

### Système Centralisé

Le projet utilise un **système centralisé** pour gérer tous les scripts et tests via `scripts/SCRIPTS_REFERENCE.py`.

**Documentation** :
- [docs/README_SCRIPTS_SYSTEM.md](docs/README_SCRIPTS_SYSTEM.md) - Guide complet
- [docs/DEPENDENCIES_MAP.md](docs/DEPENDENCIES_MAP.md) - Cartographie "qui appelle quoi"
- [docs/DEPENDENCY_GRAPH.md](docs/DEPENDENCY_GRAPH.md) - Diagrammes visuels

**Règle d'or** : ⚠️ **TOUJOURS utiliser le venv pour les tests**

---

## 🐛 Dépannage

### Erreur "Virtual environment not found"
```batch
INSTALL.bat
```

### Erreur GPU/CUDA
```batch
scripts\test_pytorch_gpu.bat
scripts\fix_pytorch_cuda.bat
```

### Tests échouent
```batch
scripts\run_test.bat test_project_integrity
```

**Plus d'aide** : [docs/HELP.md](docs/HELP.md)

---

## 📝 License

MIT License - Voir LICENSE pour plus de détails

---

## 🙏 Remerciements

- [Ultralytics YOLOv8](https://ultralytics.com/)
- [TCGdex API](https://www.tcgdex.net/)
- [OpenCV](https://opencv.org/)

---

<div align="center">

**Créé avec ❤️ pour la communauté Pokémon TCG**

*v3.2 - Novembre 2025*

</div>
