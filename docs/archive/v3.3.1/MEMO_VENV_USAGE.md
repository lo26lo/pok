# MEMO - Utilisation du venv et SCRIPTS_REFERENCE.py

## 🎯 Règle d'or

**TOUJOURS UTILISER LE VENV POUR LES TESTS ET SCRIPTS**

## 🚀 Commandes rapides

### Exécution de tests

```batch
# Un test spécifique
run_test.bat test_cuda

# Tous les tests
run_all_tests.bat

# Tests d'une catégorie
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Integration
```

### Exécution de scripts

```batch
# Un script spécifique
run_script.bat init_prices

# Avec arguments
run_script.bat merge_dataset --source1 data1 --source2 data2
```

### Lister les scripts/tests disponibles

```batch
# Liste des scripts
python scripts\SCRIPTS_REFERENCE.py --list

# Liste des tests
python scripts\SCRIPTS_REFERENCE.py --list-tests
```

## ⚠️ À NE JAMAIS FAIRE

```batch
# ❌ Exécuter un test sans venv
python tests\test_cuda.py

# ❌ Exécuter un script sans venv
python scripts\init_prices.py
```

## ✅ À TOUJOURS FAIRE

```batch
# ✅ Activer le venv puis exécuter
call .venv\Scripts\activate.bat
python tests\test_cuda.py

# ✅ OU utiliser les fichiers .bat (recommandé)
run_test.bat test_cuda
run_script.bat init_prices
```

## 📝 Maintenance de SCRIPTS_REFERENCE.py

### Lors de l'ajout d'un nouveau script

1. Créer le script dans `scripts/`
2. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
3. Ajouter l'entrée dans `SCRIPTS_CATALOG`
4. Mettre à jour le `CHANGELOG`
5. Tester avec `run_script.bat nom_du_script`

### Lors de l'ajout d'un nouveau test

1. Créer le test dans `tests/`
2. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
3. Ajouter l'entrée dans `TESTS_CATALOG`
4. Mettre à jour le `CHANGELOG`
5. Tester avec `run_test.bat nom_du_test`
6. Vérifier avec `run_all_tests.bat`

## 📂 Fichiers créés

- `scripts/SCRIPTS_REFERENCE.py` - Catalogue centralisé
- `run_all_tests.bat` - Exécute tous les tests
- `run_test.bat` - Exécute un test spécifique
- `run_script.bat` - Exécute un script spécifique
- `docs/MAINTENANCE_SCRIPTS_REFERENCE.md` - Guide complet

## 🔄 Workflow quotidien

```batch
# 1. Vérifier que le venv existe
python scripts\SCRIPTS_REFERENCE.py --check-venv

# 2. Voir les scripts/tests disponibles
python scripts\SCRIPTS_REFERENCE.py --list
python scripts\SCRIPTS_REFERENCE.py --list-tests

# 3. Exécuter ce dont vous avez besoin
run_script.bat init_prices
run_test.bat test_cuda
run_all_tests.bat

# 4. Avant chaque commit: exécuter tous les tests
run_all_tests.bat
```

## 📖 Documentation complète

Voir `docs/MAINTENANCE_SCRIPTS_REFERENCE.md` pour le guide complet.
