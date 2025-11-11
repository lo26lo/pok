# 🗺️ CARTOGRAPHIE DES DÉPENDANCES - Qui appelle quoi ?

## 📋 Vue d'ensemble

Ce fichier documente **toutes les relations d'appel** entre les différents composants du projet :
- Qui appelle quel script
- Quels modules sont importés où
- Quelle fonctionnalité dépend de quoi

**IMPORTANT** : Mettre à jour ce fichier lors de l'ajout de nouvelles dépendances !

---

## 🎨 GUI → Modules Core

### GUI_v3.1_modern.py

**Imports directs des managers core** :
```python
from core.workflow_manager import WorkflowManager, WorkflowConfig
from core.training_manager import TrainingManager, TrainingConfig
from core.detection_manager import DetectionManager, DetectionConfig
from core.image_downloader import ImageDownloader, LANGUAGES, POPULAR_SETS
```

**Appels de fonctionnalités** :

#### 📥 Onglet "Image Download"
- **Appelle** : `core.image_downloader.ImageDownloader`
  - Télécharge les images des cartes depuis TCGdex API
  - Gère les langues et les sets
  - Sauvegarde dans `images/`

#### 🎨 Onglet "Augmentation"
- **Appelle via subprocess** : `core.augmentation.py`
  - Commande : `python core/augmentation.py [args]`
  - Génère les images augmentées

#### ✨ Onglet "Holographic"
- **Appelle via subprocess** : `core.holographic_augmenter.py`
  - Commande : `python core/holographic_augmenter.py [args]`
  - Crée les effets holographiques

#### 🖼️ Onglet "Generate Mosaics"
- **Appelle via subprocess** : `core.mosaic.py`
  - Commande : `python core/mosaic.py [args]`
  - Génère les mosaïques

#### 🎯 Onglet "Training"
- **Utilise** : `core.training_manager.TrainingManager`
  - Lance l'entraînement YOLO
  - Gère les paramètres d'entraînement

#### 🔍 Onglet "Detection"
- **Utilise** : `core.detection_manager.DetectionManager`
  - Lance la détection en temps réel
  - Option "Show Prices" appelle `core.detection_with_prices.py`

#### 🔄 Onglet "Full Workflow"
- **Utilise** : `core.workflow_manager.WorkflowManager`
  - Orchestre le workflow complet
  - Appelle séquentiellement :
    1. Augmentation
    2. Holographic (optionnel)
    3. Génération mosaïques
    4. Auto-balancer
    5. Création dataset
    6. Entraînement

#### 🖼️ Onglet "Fake Images"
- **Appelle via subprocess** : `core.random_erasing.py`
  - Commande : `python core/random_erasing.py [args]`
  - Génère des images de fond avec random erasing

---

## 🔧 Fonctions Utilitaires Centralisées (core/utils.py)

**IMPORTANT** : Depuis v3.2.1, toutes les fonctions utilitaires communes sont centralisées dans `core/utils.py` pour éviter la duplication de code.

### 📋 Fonctions exportées

#### 1. `extract_card_number(filename: str) -> Optional[str]`
**Utilisé par** :
- `core/augmentation.py` - Extraction du numéro de carte depuis le nom de fichier
- `core/mosaic_optimized.py` - Idem pour génération de mosaïques
- Tout module nécessitant d'extraire le numéro de carte d'un fichier

**Formats supportés** :
- `sv08_019_en.png` → `"019"`
- `sv08_019_en_aug_042.png` → `"019"` (avec augmentation)
- `xyp_XY05_en.png` → `"XY05"`
- `pokemon_en_001_xyz.jpg` → `"001"`

#### 2. `load_card_data(source_path: str = None) -> Tuple[Dict, Dict]`
**Utilisé par** :
- `core/augmentation.py` - Chargement des données de cartes pour génération labels
- `core/mosaic_optimized.py` - Chargement pour annotations
- Tout module nécessitant les données de cartes

**Supporte** :
- YAML (prioritaire) : `models/cards_database.yaml`
- Excel (legacy) : `excel/cards_info.xlsx`
- Auto-détection du format

**Retourne** :
- `card_dict`: `{card_number: card_name}`
- `class_map`: `{card_number: class_id}`

#### 3. `resize_cards(image_paths: List[str], target_size: Tuple[int, int] = None) -> List[Tuple]`
**Utilisé par** :
- `core/augmentation.py` - Redimensionnement des images avant augmentation
- Tout module nécessitant un resize batch

**Fonctionnalités** :
- Resize automatique vers `CONFIG['target_size']` (280×380 par défaut)
- Conversion RGBA → RGB automatique
- Gestion des erreurs de chargement

#### 4. Regex Patterns (exportés)
**Constantes exportées** :
- `PATTERN_NEW_FORMAT` - Format moderne (sv08_019_en.png)
- `PATTERN_OLD_FORMAT` - Format ancien (_en_001_)
- `PATTERN_FALLBACK_1` - Fallback XXX_XXX_XXX
- `PATTERN_FALLBACK_2` - Dernier recours (\d{3})

**Utilisé par** :
- `core/augmentation.py` - Si besoin d'accéder aux patterns directement
- `core/mosaic_optimized.py` - Idem
- Tout module nécessitant la logique d'extraction personnalisée

#### 5. NumPy Compatibility Patches
**Appliqué automatiquement à l'import** :
```python
from core.utils import ...  # Les patches NumPy sont appliqués
```

**Patches inclus** :
- `np.bool`, `np.int`, `np.float`, `np.complex`, `np.object`, `np.str`
- Nécessaire pour imgaug avec NumPy < 2.0

### 📦 CONFIG (configuration globale)
**Contenu** :
```python
CONFIG = {
    'target_size': (280, 380),
    'excel_file': 'excel/cards_info.xlsx',
    'base_images_dir': 'images',
    'augmented_dir': 'images_aug',
    'output_dir': 'output',
    'yolo_format': True
}
```

**Utilisé par** : Tous les modules pour accéder aux paramètres globaux

### 🔄 Migration depuis v3.2.0
**Avant (code dupliqué)** :
```python
# Dans augmentation.py
def extract_card_number(filename):
    # ... 31 lignes de code dupliqué
    
def load_card_data(source_path):
    # ... 45 lignes de code dupliqué
```

**Après (v3.2.1+)** :
```python
# Dans augmentation.py
from core.utils import extract_card_number, load_card_data
# Utilisation directe des fonctions centralisées
```

**Bénéfices** :
- ✅ ~134 lignes de code dupliqué éliminées
- ✅ Single source of truth
- ✅ Corrections de bugs centralisées
- ✅ Meilleure testabilité

---

## 📦 Modules Core → Autres Modules

### core/utils.py
```python
# Appelle/Importe :
import pandas as pd
import yaml
import cv2
import numpy as np
```

**Responsabilité** : 
- Fonctions utilitaires communes (éviter duplication)
- Patches de compatibilité NumPy
- Chargement YAML/Excel
- Extraction de numéros de cartes
- Resize batch d'images

**Exportations principales** :
- `extract_card_number()` - Extraction numéro carte
- `load_card_data()` - Chargement YAML/Excel
- `resize_cards()` - Resize avec conversion RGBA
- `safe_print()` - Print Unicode-safe
- `PATTERN_*` - Regex compilés
- `CONFIG` - Configuration globale

### core/augmentation.py
```python
# Appelle/Importe :
from core.utils import (
    safe_print,
    extract_card_number,
    load_card_data,
    resize_cards,
    PATTERN_NEW_FORMAT,
    PATTERN_OLD_FORMAT,
    PATTERN_FALLBACK_1,
    PATTERN_FALLBACK_2,
    CONFIG
)
import imgaug.augmenters as iaa
import cv2
import numpy as np
```

**Responsabilité** : Augmentation d'images avec imgaug

**Dépendances de core/utils** :
- ✅ `extract_card_number()` - Extraction numéro depuis filename
- ✅ `load_card_data()` - Chargement données cartes
- ✅ `resize_cards()` - Resize avant augmentation
- ✅ NumPy patches - Compatibilité imgaug

### core/mosaic_optimized.py
```python
# Appelle/Importe :
from core.utils import (
    safe_print,
    extract_card_number,
    load_card_data,
    PATTERN_NEW_FORMAT,
    PATTERN_OLD_FORMAT,
    PATTERN_FALLBACK_1,
    PATTERN_FALLBACK_2,
    CONFIG
)
import cv2
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor
```

**Responsabilité** : Génération de mosaïques optimisée (GPU/CPU)

**Dépendances de core/utils** :
- ✅ `extract_card_number()` - Extraction numéro pour annotations
- ✅ `load_card_data()` - Chargement données cartes
- ✅ `safe_print()` - Affichage progression

### core/workflow_manager.py
```python
# Appelle/Importe :
from core.augmentation import augment_images_enhanced
from core.holographic_augmenter_optimized import HolographicAugmenterOptimized
from core.mosaic_optimized import generate_mosaics
from core.auto_balancer_optimized import balance_dataset_smart
from core.dataset_exporter import export_to_yolo_format
from ultralytics import YOLO
```

**Responsabilité** : Orchestrer le workflow complet

### core/training_manager.py
```python
# Appelle/Importe :
from ultralytics import YOLO
```

**Responsabilité** : Gérer l'entraînement YOLO

### core/detection_manager.py
```python
# Appelle/Importe :
from ultralytics import YOLO
import cv2
```

**Responsabilité** : Gérer la détection en temps réel

### core/detection_with_prices.py
```python
# Appelle/Importe :
from core.utils import load_prices_from_excel, safe_print
from core.card_mapping import get_card_id_from_class_name
from ultralytics import YOLO
import cv2
```

**Responsabilité** : Détection avec affichage des prix

### core/image_downloader.py
```python
# Appelle/Importe :
from core.tcgdex_api import TCGdexAPI
import requests
```

**Responsabilité** : Télécharger les images de cartes

### core/card_mapping.py
```python
# Appelle/Importe :
import json
from pathlib import Path
```

**Responsabilité** : Mapper les noms de classes YOLO ↔ IDs TCGdex

### core/utils.py
```python
# Appelle/Importe :
import pandas as pd
import yaml
```

**Responsabilité** : Fonctions utilitaires (chargement Excel, YAML, etc.)

### core/tcgdex_api.py
```python
# Appelle/Importe :
import requests
```

**Responsabilité** : Interface avec l'API TCGdex

---

## 🔧 Scripts → Modules Core

### scripts/init_prices.py
```python
# Appelle/Importe :
import yaml
import pandas as pd
from pathlib import Path
```

**Responsabilité** : Initialiser les prix depuis `data.yaml` → Excel

**Appelé par** :
- Manuellement via `run_script.bat init_prices`
- Après téléchargement d'images (workflow)

### scripts/create_card_mapping.py
```python
# Appelle/Importe :
import yaml
import json
```

**Responsabilité** : Créer le mapping `card_name_to_id.json`

**Appelé par** :
- Manuellement via `run_script.bat create_card_mapping`
- Après création du dataset

### scripts/workflow_optimized.py
```python
# Appelle/Importe :
from core.workflow_manager import WorkflowManager
```

**Responsabilité** : Lancer le workflow complet en CLI

**Appelé par** :
- Manuellement via `run_script.bat workflow_optimized`

---

## 🧪 Tests → Modules Core

### tests/test_project_integrity.py
```python
# Teste :
- Structure des dossiers
- Présence des fichiers essentiels
- Imports des modules core
```

**Appelé par** :
- `run_test.bat test_project_integrity`
- `run_all_tests.bat`

### tests/test_workflow_simulation.py
```python
# Appelle/Importe :
from core.tcgdex_api import TCGdexAPI
import cv2
import requests
```

**Responsabilité** : Simuler le workflow complet

**Appelé par** :
- `run_test.bat test_workflow_simulation`
- `run_all_tests.bat`

### tests/test_detection_prices.py
```python
# Appelle/Importe :
from core.detection_with_prices import detect_with_prices
import cv2
```

**Responsabilité** : Tester la détection avec prix

**Appelé par** :
- `run_test.bat test_detection_prices`

### tests/test_cuda.py
```python
# Appelle/Importe :
import torch
```

**Responsabilité** : Tester la disponibilité CUDA/GPU

**Appelé par** :
- `run_test.bat test_cuda`
- `test_pytorch_gpu.bat`

---

## 🎯 Workflows Complets

### Workflow 1 : Téléchargement → Entraînement

```
GUI_v3.1_modern.py (Image Download)
    ↓
core/image_downloader.py
    ↓
core/tcgdex_api.py → API TCGdex
    ↓
images/*.png (téléchargées)
    ↓
scripts/init_prices.py (manuel)
    ↓
excel/cards_with_prices.xlsx
    ↓
scripts/create_card_mapping.py (manuel)
    ↓
card_name_to_id.json
    ↓
GUI_v3.1_modern.py (Full Workflow)
    ↓
core/workflow_manager.py
    ├→ core/augmentation.py
    ├→ core/holographic_augmenter.py (optionnel)
    ├→ core/mosaic.py
    ├→ core/auto_balancer.py
    └→ core/dataset_exporter.py
    ↓
output/dataset/data.yaml
    ↓
core/training_manager.py
    ↓
runs/train/weights/best.pt
```

### Workflow 2 : Détection avec Prix

```
GUI_v3.1_modern.py (Detection tab, "Show Prices" activé)
    ↓
core/detection_manager.py
    ↓
core/detection_with_prices.py
    ├→ core/card_mapping.get_card_id_from_class_name()
    └→ core/utils.load_prices_from_excel()
    ↓
excel/cards_with_prices.xlsx
    ↓
Affichage prix en temps réel sur webcam
```

### Workflow 3 : Génération de Backgrounds

```
GUI_v3.1_modern.py (Fake Images tab)
    ↓
core/random_erasing.py (subprocess)
    ↓
backgrounds/original/*.jpg
    ↓
backgrounds/augmented/*.jpg
```

---

## 📊 Matrice de Dépendances

| Composant | Dépend de (modules core) | Appelé par |
|-----------|-------------------------|------------|
| **GUI_v3.1_modern.py** | workflow_manager, training_manager, detection_manager, image_downloader | run_gui_v3.1.bat, Pokemon_Dataset_Generator.bat |
| **core/workflow_manager.py** | augmentation, holographic_augmenter, mosaic, auto_balancer, dataset_exporter | GUI, scripts/workflow_optimized.py |
| **core/training_manager.py** | ultralytics.YOLO | GUI, workflow_manager |
| **core/detection_manager.py** | ultralytics.YOLO, cv2 | GUI |
| **core/detection_with_prices.py** | utils, card_mapping, ultralytics.YOLO, cv2 | detection_manager, tests |
| **core/image_downloader.py** | tcgdex_api | GUI |
| **core/tcgdex_api.py** | requests | image_downloader, tests |
| **core/card_mapping.py** | json | detection_with_prices, utils |
| **core/utils.py** | pandas, yaml | detection_with_prices, scripts |
| **core/augmentation.py** | cv2, numpy | workflow_manager, GUI (subprocess) |
| **core/holographic_augmenter.py** | cv2, numpy | workflow_manager, GUI (subprocess) |
| **core/mosaic.py** | cv2, numpy | workflow_manager, GUI (subprocess) |
| **core/auto_balancer.py** | - | workflow_manager |
| **core/dataset_exporter.py** | yaml | workflow_manager |
| **core/random_erasing.py** | cv2, numpy | GUI (subprocess) |

---

## 🔗 Dépendances Externes (Packages Python)

### Packages critiques

- **ultralytics** : YOLO detection et training
  - Utilisé par : training_manager, detection_manager, detection_with_prices
  
- **opencv-python (cv2)** : Traitement d'image
  - Utilisé par : augmentation, holographic_augmenter, mosaic, detection_manager, random_erasing
  
- **pandas** : Manipulation Excel
  - Utilisé par : utils, scripts/init_prices.py
  
- **requests** : Appels API
  - Utilisé par : tcgdex_api, image_downloader
  
- **PyYAML** : Lecture/écriture YAML
  - Utilisé par : utils, dataset_exporter, scripts
  
- **torch** : PyTorch (backend YOLO)
  - Utilisé par : ultralytics, tests/test_cuda.py
  
- **tkinter** : Interface GUI
  - Utilisé par : GUI_v3.1_modern.py
  
- **openpyxl** : Lecture/écriture Excel (.xlsx)
  - Utilisé par : pandas, utils

---

## 🚨 Points d'Attention

### Dépendances Circulaires

❌ **Aucune détectée** - Architecture saine

### Couplage Fort

⚠️ **GUI ↔ Core Managers** : Le GUI dépend fortement des managers
- **Risque** : Modification d'un manager peut casser le GUI
- **Solution** : Maintenir les interfaces stables (WorkflowConfig, TrainingConfig, etc.)

### Appels Subprocess

⚠️ **GUI → Scripts via subprocess** : 
- augmentation.py
- holographic_augmenter.py
- mosaic.py
- random_erasing.py

**Risque** : Chemins relatifs peuvent casser
**Solution** : Utiliser `sys.path` ou chemins absolus

---

## 📝 Règles de Maintenance

### Lors de l'ajout d'une nouvelle dépendance :

1. ✅ Mettre à jour ce fichier (DEPENDENCIES_MAP.md)
2. ✅ Mettre à jour SCRIPTS_REFERENCE.py (liste des dépendances)
3. ✅ Mettre à jour requirements.txt si nouveau package
4. ✅ Documenter dans README.md si impact utilisateur
5. ✅ Tester avec `run_all_tests.bat`

### Lors de la modification d'une interface :

1. ✅ Vérifier tous les appelants (voir matrice ci-dessus)
2. ✅ Mettre à jour les tests
3. ✅ Mettre à jour CHANGELOG.md
4. ✅ Documenter le breaking change si nécessaire

### Lors de la refactorisation :

1. ✅ Identifier toutes les dépendances (ce fichier)
2. ✅ Créer des interfaces de compatibilité si nécessaire
3. ✅ Migrer progressivement
4. ✅ Tester à chaque étape

---

## 🔍 Comment Tracer une Dépendance ?

### Exemple : "Qui utilise TCGdex API ?"

1. **Rechercher dans ce fichier** : `tcgdex_api`
2. **Trouver les appelants** :
   - `core/image_downloader.py`
   - `tests/test_workflow_simulation.py`
3. **Remonter la chaîne** :
   - `image_downloader.py` ← `GUI_v3.1_modern.py` (Image Download tab)
   - Donc : **GUI → image_downloader → tcgdex_api → API externe**

### Exemple : "Qu'est-ce qui dépend de OpenCV ?"

1. **Rechercher** : "opencv-python" dans la matrice
2. **Modules dépendants** :
   - augmentation.py
   - holographic_augmenter.py
   - mosaic.py
   - detection_manager.py
   - random_erasing.py
3. **Impact** : Si OpenCV casse, 5 modules impactés

---

## 📈 Graphe de Dépendances (ASCII)

```
                    ┌─────────────────────┐
                    │   GUI_v3.1_modern   │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼────────┐  ┌─────▼──────┐  ┌───────▼────────┐
    │ workflow_mgr   │  │ training_  │  │ detection_     │
    │                │  │ manager    │  │ manager        │
    └───────┬────────┘  └─────┬──────┘  └───────┬────────┘
            │                 │                  │
    ┌───────┼─────────┐       │         ┌────────┼─────────┐
    │       │         │       │         │        │         │
┌───▼───┐ ┌▼──────┐ ┌▼───────▼┐    ┌──▼───────┐ ┌───────▼──────┐
│augment│ │holo   │ │ mosaic  │    │ YOLO     │ │ detection_   │
│       │ │graphic│ │         │    │          │ │ with_prices  │
└───────┘ └───────┘ └─────────┘    └──────────┘ └──────┬───────┘
                                                         │
                                                  ┌──────┼──────┐
                                                  │      │      │
                                             ┌────▼──┐ ┌▼──────▼┐
                                             │ utils │ │ card_  │
                                             │       │ │ mapping│
                                             └───────┘ └────────┘
```

---

## 🎯 Prochaines Étapes

### Pour améliorer la modularité :

1. **Créer des interfaces abstraites** pour les managers
2. **Ajouter un système de plugins** pour les augmentations
3. **Implémenter un bus d'événements** pour découpler GUI ↔ Core
4. **Créer un système de configuration central** (éviter duplication gui_config.json, data.yaml, etc.)

### Pour faciliter la maintenance :

1. **Automatiser la génération de ce fichier** (parsing des imports)
2. **Créer des tests de dépendances** (vérifier qu'aucune circulaire n'existe)
3. **Documenter les API publiques** de chaque module core
4. **Créer un diagramme de dépendances visuel** (avec graphviz)

---

**Dernière mise à jour** : 2025-11-10  
**Maintenu par** : Projet Pokémon Dataset Generator  
**Version** : 1.0

**⚠️ IMPORTANT : Mettre à jour ce fichier lors de l'ajout/modification de dépendances !**
