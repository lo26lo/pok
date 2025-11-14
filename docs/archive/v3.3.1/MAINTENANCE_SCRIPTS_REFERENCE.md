# GUIDE DE MAINTENANCE - SCRIPTS_REFERENCE.py

## 📋 Vue d'ensemble

Le fichier `scripts/SCRIPTS_REFERENCE.py` est le **catalogue centralisé** de tous les scripts et tests du projet. Il DOIT être maintenu à jour à chaque modification.

## ⚠️ RÈGLES IMPÉRATIVES

### 1. Toujours utiliser le venv

**TOUS les tests DOIVENT être exécutés dans le venv (.venv)**

```batch
# ❌ INCORRECT - Ne jamais faire
python tests/test_cuda.py

# ✅ CORRECT - Toujours utiliser
call .venv\Scripts\activate.bat
python tests/test_cuda.py

# ✅ OU utiliser les fichiers .bat fournis
run_test.bat test_cuda
```

### 2. Mettre à jour SCRIPTS_REFERENCE.py

À **CHAQUE** ajout, modification ou suppression de script/test :

1. **Ouvrir** `scripts/SCRIPTS_REFERENCE.py`
2. **Localiser** la section appropriée (`SCRIPTS_CATALOG` ou `TESTS_CATALOG`)
3. **Mettre à jour** l'entrée correspondante
4. **Documenter** le changement dans la section `CHANGELOG` en haut du fichier

## 📝 Quand mettre à jour SCRIPTS_REFERENCE.py

### Ajout d'un nouveau script

```python
# Dans SCRIPTS_CATALOG
"mon_nouveau_script": {
    "path": SCRIPTS_DIR / "mon_nouveau_script.py",
    "description": "Description claire de ce que fait le script",
    "category": "Category appropriée",  # Configuration, Data Processing, Debug, Workflow, etc.
    "dependencies": ["pandas", "numpy"],  # Liste des packages requis
    "arguments": ["--input", "--output"],  # Arguments acceptés
    "requires_venv": True,  # True si nécessite le venv
    "last_modified": "2025-11-10"  # Date de dernière modification
}
```

### Ajout d'un nouveau test

```python
# Dans TESTS_CATALOG
"test_nouvelle_fonctionnalite": {
    "path": TESTS_DIR / "test_nouvelle_fonctionnalite.py",
    "description": "Teste la nouvelle fonctionnalité X",
    "category": "Features",  # Hardware, Integration, Features, Training, Performance, Debug, Validation, Visualization
    "dependencies": ["opencv-python", "torch"],
    "requires_venv": True,  # TOUJOURS True pour les tests
    "last_modified": "2025-11-10"
}
```

### Modification d'un script existant

1. **Trouver l'entrée** dans le catalogue
2. **Mettre à jour** les champs modifiés (description, dépendances, arguments)
3. **Changer** la date `last_modified`
4. **Ajouter** une ligne dans le `CHANGELOG` en haut du fichier

```python
# En haut de SCRIPTS_REFERENCE.py
CHANGELOG:
----------
2025-11-10: Modification de init_prices.py - ajout argument --format
2025-11-10: Création du fichier référence centralisé
```

### Suppression d'un script

1. **Retirer l'entrée** du catalogue
2. **Documenter** dans le `CHANGELOG`

## 🔧 Utilisation quotidienne

### Lister les scripts disponibles

```batch
# Voir tous les scripts
python scripts\SCRIPTS_REFERENCE.py --list

# Voir tous les tests
python scripts\SCRIPTS_REFERENCE.py --list-tests
```

### Exécuter un script

```batch
# Méthode 1: Via le gestionnaire (recommandé)
run_script.bat init_prices

# Méthode 2: Via Python
python scripts\SCRIPTS_REFERENCE.py --run init_prices

# Avec arguments
run_script.bat merge_dataset --source1 data1 --source2 data2
```

### Exécuter un test

```batch
# Méthode 1: Via le gestionnaire (recommandé)
run_test.bat test_cuda

# Méthode 2: Via Python
python scripts\SCRIPTS_REFERENCE.py --test test_cuda
```

### Exécuter tous les tests

```batch
# Tous les tests
run_all_tests.bat

# Ou via Python
python scripts\SCRIPTS_REFERENCE.py --run-all-tests

# Tests d'une catégorie spécifique
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Integration
python scripts\SCRIPTS_REFERENCE.py --run-all-tests --category Performance
```

## 📂 Structure des catalogues

### Catégories de scripts

- **Configuration**: Scripts d'initialisation et configuration (init_prices, etc.)
- **Data Processing**: Traitement de données (create_card_mapping, merge_dataset, etc.)
- **Debug**: Scripts de débogage (debug_excel_keys, fix_class_mapping, etc.)
- **Workflow**: Workflows complets (workflow_optimized, etc.)
- **Migration**: Scripts de migration de structure
- **Maintenance**: Nettoyage et maintenance

### Catégories de tests

- **Hardware**: Tests matériel (CUDA, GPU)
- **Integration**: Tests d'intégration (test_project_integrity, test_workflow_simulation)
- **Features**: Tests de fonctionnalités (test_detection_prices)
- **Training**: Tests d'entraînement (test_gpu_training)
- **Performance**: Benchmarks de performance (test_mosaic_performance, etc.)
- **Debug**: Tests de débogage (test_mapping_debug)
- **Validation**: Validation de données (verify_data_yaml, check_corrupted_images)
- **Visualization**: Tests de visualisation (visualize_annotations, visualize_bbox)

## 🎯 Workflow de développement

### 1. Créer un nouveau script

```bash
# 1. Créer le fichier
scripts/mon_nouveau_script.py

# 2. Développer le script
# ... code ...

# 3. Mettre à jour SCRIPTS_REFERENCE.py
# Ajouter l'entrée dans SCRIPTS_CATALOG

# 4. Tester
run_script.bat mon_nouveau_script

# 5. Committer
git add scripts/mon_nouveau_script.py scripts/SCRIPTS_REFERENCE.py
git commit -m "feat: add mon_nouveau_script for X functionality"
```

### 2. Créer un nouveau test

```bash
# 1. Créer le fichier
tests/test_ma_fonctionnalite.py

# 2. Développer le test
# ... code ...

# 3. Mettre à jour SCRIPTS_REFERENCE.py
# Ajouter l'entrée dans TESTS_CATALOG

# 4. Tester dans le venv
run_test.bat test_ma_fonctionnalite

# 5. Vérifier avec tous les tests
run_all_tests.bat

# 6. Committer
git add tests/test_ma_fonctionnalite.py scripts/SCRIPTS_REFERENCE.py
git commit -m "test: add test_ma_fonctionnalite"
```

### 3. Modifier un script existant

```bash
# 1. Modifier le script
# ... modifications ...

# 2. Mettre à jour SCRIPTS_REFERENCE.py
# - Modifier la description si nécessaire
# - Mettre à jour les dépendances si changées
# - Mettre à jour last_modified
# - Ajouter une ligne au CHANGELOG

# 3. Tester
run_script.bat nom_du_script

# 4. Committer
git add scripts/nom_du_script.py scripts/SCRIPTS_REFERENCE.py
git commit -m "refactor: update nom_du_script - description des changements"
```

## ✅ Checklist avant commit

Avant chaque commit impliquant des scripts/tests :

- [ ] ✅ Le script/test fonctionne dans le venv
- [ ] ✅ SCRIPTS_REFERENCE.py est mis à jour
- [ ] ✅ La date `last_modified` est correcte
- [ ] ✅ Le CHANGELOG contient une entrée
- [ ] ✅ Les tests passent (`run_all_tests.bat`)
- [ ] ✅ Le fichier est dans le bon répertoire (`scripts/` ou `tests/`)
- [ ] ✅ Les dépendances sont listées

## 🚫 Erreurs courantes à éviter

### ❌ Exécuter un test hors du venv

```batch
# ❌ INCORRECT
python tests/test_cuda.py
```

**Solution**: Toujours utiliser `run_test.bat` ou activer le venv

### ❌ Oublier de mettre à jour SCRIPTS_REFERENCE.py

Chaque nouveau fichier doit être ajouté au catalogue, sinon :
- Impossible d'utiliser `run_script.bat` ou `run_test.bat`
- Pas de documentation centralisée
- Risque d'oubli lors des migrations

**Solution**: Ajouter systématiquement l'entrée

### ❌ Dépendances incorrectes

```python
# ❌ INCORRECT
"dependencies": [],  # Mais le script utilise pandas

# ✅ CORRECT
"dependencies": ["pandas", "openpyxl"],
```

**Solution**: Lister TOUTES les dépendances importées

### ❌ Catégorie inappropriée

```python
# ❌ INCORRECT - Un test de validation en "Performance"
"category": "Performance",

# ✅ CORRECT
"category": "Validation",
```

**Solution**: Choisir la catégorie qui correspond au rôle principal

## 🔍 Vérification de l'intégrité

### Vérifier que le venv existe

```batch
python scripts\SCRIPTS_REFERENCE.py --check-venv
```

### Vérifier tous les fichiers référencés

```python
# Dans SCRIPTS_REFERENCE.py, tous les chemins existent
for name, info in SCRIPTS_CATALOG.items():
    assert info["path"].exists(), f"Fichier manquant: {name}"
```

### Vérifier que tous les scripts/tests sont catalogués

```bash
# Lister tous les .py dans scripts/
dir scripts\*.py

# Comparer avec SCRIPTS_REFERENCE.py --list
python scripts\SCRIPTS_REFERENCE.py --list
```

## 📊 Exemples pratiques

### Exemple 1: Ajouter un script de nettoyage

```python
# Dans SCRIPTS_REFERENCE.py
"cleanup_annotations": {
    "path": SCRIPTS_DIR / "cleanup_annotations.py",
    "description": "Nettoie les annotations invalides du dataset",
    "category": "Maintenance",
    "dependencies": ["PyYAML"],
    "arguments": ["--dataset"],
    "requires_venv": True,
    "last_modified": "2025-11-10"
}
```

### Exemple 2: Ajouter un test de régression

```python
# Dans SCRIPTS_REFERENCE.py
"test_regression_v3": {
    "path": TESTS_DIR / "test_regression_v3.py",
    "description": "Tests de non-régression pour la v3.1",
    "category": "Integration",
    "dependencies": ["ultralytics", "opencv-python", "pandas"],
    "requires_venv": True,
    "last_modified": "2025-11-10"
}
```

### Exemple 3: Modifier un script existant

```python
# AVANT
"init_prices": {
    "path": SCRIPTS_DIR / "init_prices.py",
    "description": "Initialise les prix des cartes depuis data.yaml vers Excel",
    "dependencies": ["pandas", "openpyxl", "PyYAML"],
    "arguments": [],
    "last_modified": "2025-11-10"
}

# APRÈS (ajout d'un argument)
"init_prices": {
    "path": SCRIPTS_DIR / "init_prices.py",
    "description": "Initialise les prix des cartes depuis data.yaml vers Excel",
    "dependencies": ["pandas", "openpyxl", "PyYAML"],
    "arguments": ["--format", "--output"],  # ✅ Nouveau
    "last_modified": "2025-11-15"  # ✅ Date mise à jour
}

# Et dans le CHANGELOG en haut:
# 2025-11-15: Modification de init_prices - ajout arguments --format et --output
```

## 🎓 Formation de l'équipe

Lors de l'ajout d'un nouveau développeur :

1. ✅ Lui faire lire ce guide
2. ✅ Lui montrer `run_script.bat --help`
3. ✅ Lui expliquer l'importance du venv
4. ✅ Faire un exercice : ajouter un script de test et le cataloguer
5. ✅ Vérifier qu'il comprend le workflow avant le commit

## 📞 Support

En cas de problème avec SCRIPTS_REFERENCE.py :

1. Vérifier que le venv existe (`install_env.bat`)
2. Vérifier que tous les chemins sont corrects
3. Vérifier que les dépendances sont installées
4. Consulter ce guide
5. Exécuter `run_all_tests.bat` pour identifier les problèmes

## 🔄 Maintenance régulière

### Hebdomadaire
- [ ] Vérifier que tous les tests passent (`run_all_tests.bat`)
- [ ] Vérifier que les dépendances sont à jour

### Mensuel
- [ ] Revoir les catégories et réorganiser si nécessaire
- [ ] Nettoyer les scripts obsolètes
- [ ] Mettre à jour la documentation

### Avant chaque release
- [ ] Tous les tests passent
- [ ] SCRIPTS_REFERENCE.py est à jour
- [ ] Toutes les dépendances sont documentées
- [ ] Le CHANGELOG est complet
