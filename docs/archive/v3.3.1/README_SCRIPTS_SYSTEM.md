# 🚀 Système de Gestion Centralisée des Scripts et Tests

## 📋 Vue d'ensemble

Ce projet utilise maintenant un **système centralisé** pour gérer tous les scripts et tests via le fichier `scripts/SCRIPTS_REFERENCE.py`.

### ✨ Avantages

- ✅ **Catalogue unique** : Tous les scripts et tests sont documentés dans un seul fichier
- ✅ **Cartographie des dépendances** : Visualisation complète de qui appelle quoi
- ✅ **Utilisation du venv garantie** : Tous les tests s'exécutent dans l'environnement virtuel
- ✅ **Exécution simplifiée** : Fichiers .bat pour lancer n'importe quel script/test
- ✅ **Traçabilité** : CHANGELOG intégré pour suivre les modifications
- ✅ **Documentation automatique** : Liste des dépendances et descriptions

## 📚 Documentation Complète

| Fichier | Description |
|---------|-------------|
| **README_SCRIPTS_SYSTEM.md** (ce fichier) | Guide d'utilisation principal |
| **DEPENDENCIES_MAP.md** | Cartographie complète : Qui appelle quoi ? |
| **docs/DEPENDENCY_GRAPH.md** | Diagrammes visuels interactifs (Mermaid) |
| **docs/MAINTENANCE_SCRIPTS_REFERENCE.md** | Guide de maintenance détaillé |
| **MEMO_VENV_USAGE.md** | Mémo rapide pour l'usage quotidien |
| **CHECKLIST_MODIFICATIONS.md** | Checklist lors de modifications |

## 🎯 Règle d'or

**TOUJOURS UTILISER LE VENV POUR LES TESTS ET SCRIPTS**

## 🚀 Démarrage rapide

### 1. Installation de l'environnement

```batch
install_env.bat
```

### 2. Vérifier que le venv fonctionne

```batch
python scripts\SCRIPTS_REFERENCE.py --check-venv
```

### 3. Lancer tous les tests

```batch
run_all_tests.bat
```

## 📚 Commandes disponibles

### Lister les scripts et tests

```batch
# Liste tous les scripts disponibles par catégorie
python scripts\SCRIPTS_REFERENCE.py --list

# Liste tous les tests disponibles par catégorie
python scripts\SCRIPTS_REFERENCE.py --list-tests
```

### Exécuter un script

```batch
# Méthode recommandée (via .bat)
run_script.bat init_prices

# Méthode alternative (via Python)
python scripts\SCRIPTS_REFERENCE.py --run init_prices

# Avec des arguments
run_script.bat merge_dataset --source1 data1 --source2 data2
```

### Exécuter un test

```batch
# Méthode recommandée (via .bat)
run_test.bat test_cuda

# Méthode alternative (via Python)
python scripts\SCRIPTS_REFERENCE.py --test test_cuda
```

### Exécuter tous les tests

```batch
# Tous les tests
run_all_tests.bat

# OU via Python
python scripts\SCRIPTS_REFERENCE.py --run-all-tests

# Filtrer par catégorie
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Integration
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Performance
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Validation
```

## 📂 Structure des fichiers

```
pok/
├── scripts/
│   ├── SCRIPTS_REFERENCE.py      # 🔥 Catalogue centralisé (À MAINTENIR)
│   ├── init_prices.py
│   ├── create_card_mapping.py
│   └── ...
├── tests/
│   ├── test_cuda.py
│   ├── test_project_integrity.py
│   └── ...
├── docs/
│   ├── MAINTENANCE_SCRIPTS_REFERENCE.md  # Guide complet
│   └── ...
├── run_all_tests.bat             # Exécute tous les tests
├── run_test.bat                  # Exécute un test spécifique
├── run_script.bat                # Exécute un script spécifique
└── MEMO_VENV_USAGE.md            # Mémo rapide
```

## 🔧 Catégories de scripts

### Configuration
- `init_prices` : Initialise les prix depuis data.yaml
- `init_prices_real` : Initialise les prix réels depuis TCGdex API
- `init_prices_simple` : Version simplifiée

### Data Processing
- `create_card_mapping` : Crée le mapping classe ↔ TCGdex ID
- `merge_dataset` : Fusionne plusieurs datasets
- `read_excel_mapping` : Lit le mapping Excel

### Debug
- `debug_excel_keys` : Debug les clés Excel
- `fix_class_mapping` : Corrige les mappings

### Workflow
- `workflow_optimized` : Workflow complet optimisé

## 🧪 Catégories de tests

### Hardware
- `test_cuda` : Teste CUDA/GPU

### Integration
- `test_project_integrity` : Intégrité complète
- `test_workflow_simulation` : Simule le workflow
- `test_full_chain` : Chaîne complète

### Features
- `test_detection_prices` : Détection avec prix

### Performance
- `test_autobalancer_performance` : Benchmark auto-balancer
- `test_holographic_performance` : Benchmark holographique
- `test_mosaic_performance` : Benchmark mosaïques

### Validation
- `verify_data_yaml` : Vérifie data.yaml
- `check_corrupted_images` : Vérifie les images
- `verify_detailed` : Vérification détaillée

### Visualization
- `visualize_annotations` : Visualise les annotations
- `visualize_bbox` : Visualise les bounding boxes

## 📝 Maintenance

### Ajouter un nouveau script

1. Créer le script dans `scripts/mon_script.py`
2. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
3. Ajouter une entrée dans `SCRIPTS_CATALOG` :

```python
"mon_script": {
    "path": SCRIPTS_DIR / "mon_script.py",
    "description": "Description claire",
    "category": "Configuration",  # ou Data Processing, Debug, etc.
    "dependencies": ["pandas", "numpy"],
    "arguments": ["--input", "--output"],
    "requires_venv": True,
    "last_modified": "2025-11-10"
}
```

4. Mettre à jour le `CHANGELOG` en haut du fichier
5. Tester : `run_script.bat mon_script`

### Ajouter un nouveau test

1. Créer le test dans `tests/test_ma_fonctionnalite.py`
2. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
3. Ajouter une entrée dans `TESTS_CATALOG` :

```python
"test_ma_fonctionnalite": {
    "path": TESTS_DIR / "test_ma_fonctionnalite.py",
    "description": "Teste ma fonctionnalité",
    "category": "Features",  # ou Integration, Performance, etc.
    "dependencies": ["opencv-python"],
    "requires_venv": True,  # TOUJOURS True pour les tests
    "last_modified": "2025-11-10"
}
```

4. Mettre à jour le `CHANGELOG`
5. Tester : `run_test.bat test_ma_fonctionnalite`
6. Vérifier : `run_all_tests.bat`

## ⚠️ Règles importantes

### ❌ À NE JAMAIS FAIRE

```batch
# Exécuter un test sans venv
python tests\test_cuda.py

# Oublier de mettre à jour SCRIPTS_REFERENCE.py
# (Ajouter un script sans l'enregistrer dans le catalogue)

# Modifier un script sans mettre à jour sa documentation
```

### ✅ À TOUJOURS FAIRE

```batch
# Utiliser les fichiers .bat
run_test.bat test_cuda
run_script.bat init_prices

# OU activer le venv manuellement
call .venv\Scripts\activate.bat
python tests\test_cuda.py

# Mettre à jour SCRIPTS_REFERENCE.py à chaque modification
```

## 🔍 Vérifications avant commit

Avant chaque commit :

```batch
# 1. Vérifier que tous les tests passent
run_all_tests.bat

# 2. Vérifier que SCRIPTS_REFERENCE.py est à jour
python scripts\SCRIPTS_REFERENCE.py --list
python scripts\SCRIPTS_REFERENCE.py --list-tests

# 3. Vérifier le venv
python scripts\SCRIPTS_REFERENCE.py --check-venv
```

## 📖 Documentation complète

- **Guide de maintenance** : `docs/MAINTENANCE_SCRIPTS_REFERENCE.md`
- **Mémo rapide** : `MEMO_VENV_USAGE.md`
- **Ce fichier** : `README_SCRIPTS_SYSTEM.md`

## 🎓 Exemples pratiques

### Workflow typique

```batch
# 1. Initialiser l'environnement
install_env.bat

# 2. Télécharger des images (via GUI ou script)
run_gui_v3.1.bat

# 3. Initialiser les prix
run_script.bat init_prices

# 4. Créer le mapping
run_script.bat create_card_mapping

# 5. Vérifier avec les tests
run_test.bat test_project_integrity
run_test.bat test_workflow_simulation
run_all_tests.bat

# 6. Lancer l'entraînement
run_script.bat workflow_optimized
```

### Tests de performance

```batch
# Tester toutes les performances
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Performance

# Ou individuellement
run_test.bat test_mosaic_performance
run_test.bat test_holographic_performance
run_test.bat test_autobalancer_performance
```

### Validation du dataset

```batch
# Tests de validation
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Validation

# Ou individuellement
run_test.bat verify_data_yaml
run_test.bat check_corrupted_images
run_test.bat verify_detailed
```

## 🆘 Dépannage

### Le venv n'existe pas

```batch
install_env.bat
```

### Un test échoue

```batch
# Exécuter uniquement ce test pour voir les détails
run_test.bat nom_du_test

# Vérifier les dépendances
call .venv\Scripts\activate.bat
pip list
```

### Un script n'apparaît pas dans la liste

Vérifier qu'il est bien enregistré dans `scripts/SCRIPTS_REFERENCE.py` dans le catalogue approprié (`SCRIPTS_CATALOG` ou `TESTS_CATALOG`).

## 🔄 Mise à jour du système

Si vous modifiez `SCRIPTS_REFERENCE.py` :

1. Mettre à jour le `CHANGELOG` en haut du fichier
2. Tester que le système fonctionne :
   ```batch
   python scripts\SCRIPTS_REFERENCE.py --list
   python scripts\SCRIPTS_REFERENCE.py --list-tests
   python scripts\SCRIPTS_REFERENCE.py --check-venv
   ```
3. Exécuter tous les tests :
   ```batch
   run_all_tests.bat
   ```
4. Committer avec un message clair :
   ```batch
   git add scripts/SCRIPTS_REFERENCE.py
   git commit -m "docs: update SCRIPTS_REFERENCE - add script X"
   ```

## 📞 Support

En cas de problème :

1. Consulter `docs/MAINTENANCE_SCRIPTS_REFERENCE.md`
2. Vérifier `MEMO_VENV_USAGE.md`
3. Exécuter `python scripts\SCRIPTS_REFERENCE.py --check-venv`
4. Relancer `install_env.bat`

---

**Créé le**: 2025-11-10  
**Dernière mise à jour**: 2025-11-10  
**Version**: 1.0
