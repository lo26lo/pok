# Version 3.2.3 - Path Centralization System

**Date**: 12 novembre 2025  
**Type**: Configuration refactoring  
**Impact**: 25+ fichiers modifiés

---

## 🎯 Objectif

Centraliser TOUS les chemins de fichiers/dossiers dans un fichier JSON unique pour :
- Éliminer les paths hardcodés dans le code
- Faciliter les futures modifications de structure
- Avoir une source unique de vérité

## 📁 Nouveau Fichier

### `config/paths.json`
```json
{
  "directories": {
    "images": "images",
    "models": "models",
    "output_base": "output",
    "output_augmented": "output/augmented",
    "output_mosaics": "output/mosaics",
    "output_dataset": "output/dataset",
    // ... 24 directories au total
  },
  "files": {
    "cards_database_yaml": "models/cards_database.yaml",
    "dataset_data_yaml": "output/dataset/data.yaml",
    "best_model": "runs/train/pokemon_detector/weights/best.pt",
    // ... 15 files au total
  }
}
```

**Total**: 39 paths centralisés (24 directories + 15 files)

---

## 🔄 Pattern Utilisé

### Chaque fichier implémente :
```python
import json
from pathlib import Path

def load_paths():
    config_path = Path("config/paths.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

PATHS = load_paths()

# Utilisation
images_dir = PATHS['directories']['images']
yaml_file = PATHS['files']['cards_database_yaml']
```

### Rétrocompatibilité
Les fonctions gardent leurs signatures existantes avec `default=None` :
```python
def ma_fonction(yaml_path=None):
    if yaml_path is None:
        yaml_path = PATHS['files']['cards_database_yaml']
    # ...
```

---

## 📝 Fichiers Modifiés

### Core Modules (5 fichiers)
| Fichier | Modifications |
|---------|---------------|
| `core/utils.py` | Fonction `load_paths()`, global `PATHS`, mise à jour CONFIG |
| `core/mosaic_optimized.py` | 6 constants de paths remplacés |
| `core/augmentation.py` | 5 paths (dirs + yaml) |
| `core/random_erasing.py` | 2 argparse defaults |
| `core/detection_with_prices.py` | 6 paths (model, yaml, data-yaml) |

**Vérifiés sans paths** : card_mapping.py, tcgdex_api.py, dataset_exporter.py, auto_balancer_optimized.py

### GUI (1 fichier massif)
| Fichier | Modifications |
|---------|---------------|
| `GUI_v3.1_modern.py` | 100+ paths remplacés |

**Sections modifiées** :
- SettingsDialog defaults (7 paths)
- get_augmentation_stats() (3 paths)
- Fake image entries (2 paths)
- Open folder buttons (3 paths)
- Dataset validation (1 path)
- Detection model (1 path)
- YAML generation (2 paths)
- Stats counting (4 paths)
- Training plots (1 path)
- Browse model dialog (1 path)
- Holographic pipeline (2 paths)
- Dataset merge (1 path)
- Export/balancer (2 paths)
- Extension Tools (2 paths)
- Clean functions (6 paths)
- show_statistics() (4 paths)

### Scripts Principaux (4 fichiers)
| Fichier | Modifications |
|---------|---------------|
| `scripts/init_prices.py` | 2 paths (data_yaml, cards_database_yaml) |
| `scripts/merge_dataset.py` | 3 paths (augmented, mosaics, dataset) |
| `scripts/workflow_optimized.py` | 10+ paths (holographic, augmented, mosaics, dataset, images) |
| `scripts/update_prices_yaml_fast.py` | 2 paths (cards_database_yaml) |

### Scripts Secondaires (7 fichiers)
| Fichier | Modifications |
|---------|---------------|
| `scripts/visualize_mosaic_bbox.py` | 4 paths (cards_db, data_yaml, mosaics, visualization) |
| `scripts/update_prices_yaml.py` | 2 paths (cards_database_yaml) |
| `scripts/migrate_excel_to_yaml.py` | 3 paths (excel, yaml, backup) |
| `scripts/init_prices_simple.py` | 2 paths (cards_database_yaml) |

### Tests (2 fichiers critiques)
| Fichier | Modifications |
|---------|---------------|
| `tests/test_project_integrity.py` | Ajout load_paths(), vérification paths.json |
| `tests/test_detection_prices.py` | 3 paths (MODEL_PATH, DATA_YAML, EXCEL_PATH) |

---

## ✅ Bénéfices

### Avant (hardcodé)
```python
# ❌ Dispersé dans tout le code
yaml_path = Path("models/cards_database.yaml")
output_dir = "output/augmented/images"
model_path = "runs/train/pokemon_detector/weights/best.pt"
```

### Après (centralisé)
```python
# ✅ Une seule source de vérité
yaml_path = Path(PATHS['files']['cards_database_yaml'])
output_dir = PATHS['directories']['output_augmented_images']
model_path = PATHS['files']['best_model']
```

### Avantages
1. **Changement simplifié** : Modifier un path = éditer 1 ligne dans paths.json
2. **Cohérence garantie** : Impossible d'avoir des paths conflictuels
3. **Documentation** : paths.json documente la structure complète
4. **Maintenabilité** : Nouveau dev comprend structure en 1 fichier
5. **Évolutivité** : Facile d'ajouter nouveaux paths

---

## 🧪 Tests

Fichiers de test mis à jour pour utiliser le nouveau système :
- `test_project_integrity.py` : Vérifie existence de paths.json + charge PATHS
- `test_detection_prices.py` : Utilise PATHS pour tous les chemins

Tests d'intégrité à exécuter :
```bash
.\.venv\Scripts\Activate.ps1
python tests\test_project_integrity.py
```

---

## 📊 Statistiques

- **Fichiers créés** : 1 (config/paths.json)
- **Fichiers modifiés** : 25+
  - Core : 5
  - GUI : 1 (100+ replacements)
  - Scripts : 11
  - Tests : 2
- **Paths centralisés** : 39 (24 directories + 15 files)
- **Lignes modifiées** : ~300+
- **Temps de développement** : ~1h

---

## 🔄 Migration Future

Pour ajouter un nouveau path :
1. Ajouter dans `config/paths.json`
2. Utiliser `PATHS['directories']['nouveau']` ou `PATHS['files']['nouveau']`
3. Aucun changement de structure nécessaire

Exemple :
```json
// config/paths.json
{
  "directories": {
    "output_predictions": "output/predictions"  // Nouveau !
  }
}
```

```python
# Utilisation immédiate
predictions_dir = Path(PATHS['directories']['output_predictions'])
```

---

## 📚 Documentation Associée

- `.planning/2025-11-12_centralisation-paths.md` : Plan détaillé de l'implémentation
- `docs/README_COMPLET.md` : Section mise à jour avec nouveau système
- Ce changelog : Version 3.2.3

---

**Contributeurs** : lo26lo + GitHub Copilot  
**Branche** : feature/migrate-directories  
**Commit** : À venir (feat(config): centralize all paths in JSON config)
