# 📋 CHECKLIST - Modifications de Scripts/Tests

## ⚠️ À LIRE AVANT TOUTE MODIFICATION

Ce fichier contient la **checklist obligatoire** à suivre pour toute modification des scripts ou tests.

**Ne jamais oublier de mettre à jour `scripts/SCRIPTS_REFERENCE.py` !**

---

## ✅ Checklist pour AJOUTER un nouveau script

- [ ] 1. Créer le script dans `scripts/nom_du_script.py`
- [ ] 2. Tester le script manuellement dans le venv
- [ ] 3. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
- [ ] 4. Ajouter l'entrée dans `SCRIPTS_CATALOG` avec :
  - [ ] path
  - [ ] description claire
  - [ ] category appropriée
  - [ ] dependencies complètes
  - [ ] arguments (si applicable)
  - [ ] requires_venv
  - [ ] last_modified (date du jour)
- [ ] 5. Ajouter une ligne dans le `CHANGELOG` en haut du fichier
- [ ] 6. Tester avec : `run_script.bat nom_du_script`
- [ ] 7. Vérifier dans la liste : `python scripts\SCRIPTS_REFERENCE.py --list`
- [ ] 8. Committer ensemble :
  ```batch
  git add scripts/nom_du_script.py scripts/SCRIPTS_REFERENCE.py
  git commit -m "feat: add nom_du_script for [description]"
  ```

---

## ✅ Checklist pour AJOUTER un nouveau test

- [ ] 1. Créer le test dans `tests/test_nom.py`
- [ ] 2. Tester le test manuellement dans le venv
- [ ] 3. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
- [ ] 4. Ajouter l'entrée dans `TESTS_CATALOG` avec :
  - [ ] path
  - [ ] description claire
  - [ ] category appropriée
  - [ ] dependencies complètes
  - [ ] requires_venv = True (TOUJOURS)
  - [ ] last_modified (date du jour)
- [ ] 5. Ajouter une ligne dans le `CHANGELOG` en haut du fichier
- [ ] 6. Tester avec : `run_test.bat test_nom`
- [ ] 7. Vérifier dans la liste : `python scripts\SCRIPTS_REFERENCE.py --list-tests`
- [ ] 8. Exécuter tous les tests : `run_all_tests.bat`
- [ ] 9. Committer ensemble :
  ```batch
  git add tests/test_nom.py scripts/SCRIPTS_REFERENCE.py
  git commit -m "test: add test_nom for [description]"
  ```

---

## ✅ Checklist pour MODIFIER un script existant

- [ ] 1. Modifier le script
- [ ] 2. Tester les modifications dans le venv
- [ ] 3. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
- [ ] 4. Localiser l'entrée du script dans `SCRIPTS_CATALOG`
- [ ] 5. Mettre à jour si nécessaire :
  - [ ] description (si la fonctionnalité change)
  - [ ] dependencies (si ajout/suppression de packages)
  - [ ] arguments (si la signature change)
  - [ ] last_modified (date du jour)
- [ ] 6. Ajouter une ligne dans le `CHANGELOG` en haut du fichier
- [ ] 7. Tester : `run_script.bat nom_du_script`
- [ ] 8. Exécuter les tests associés si applicable
- [ ] 9. Committer ensemble :
  ```batch
  git add scripts/nom_du_script.py scripts/SCRIPTS_REFERENCE.py
  git commit -m "refactor: update nom_du_script - [description]"
  ```

---

## ✅ Checklist pour MODIFIER un test existant

- [ ] 1. Modifier le test
- [ ] 2. Tester les modifications dans le venv
- [ ] 3. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
- [ ] 4. Localiser l'entrée du test dans `TESTS_CATALOG`
- [ ] 5. Mettre à jour si nécessaire :
  - [ ] description (si ce qui est testé change)
  - [ ] dependencies (si ajout/suppression de packages)
  - [ ] last_modified (date du jour)
- [ ] 6. Ajouter une ligne dans le `CHANGELOG` en haut du fichier
- [ ] 7. Tester : `run_test.bat test_nom`
- [ ] 8. Exécuter tous les tests : `run_all_tests.bat`
- [ ] 9. Committer ensemble :
  ```batch
  git add tests/test_nom.py scripts/SCRIPTS_REFERENCE.py
  git commit -m "test: update test_nom - [description]"
  ```

---

## ✅ Checklist pour SUPPRIMER un script

- [ ] 1. Vérifier qu'aucun autre script ne dépend de celui-ci
- [ ] 2. Vérifier qu'aucun fichier .bat ne l'appelle
- [ ] 3. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
- [ ] 4. Supprimer l'entrée dans `SCRIPTS_CATALOG`
- [ ] 5. Ajouter une ligne dans le `CHANGELOG` : "Suppression de [nom] - [raison]"
- [ ] 6. Vérifier la liste : `python scripts\SCRIPTS_REFERENCE.py --list`
- [ ] 7. Supprimer le fichier
- [ ] 8. Exécuter les tests : `run_all_tests.bat`
- [ ] 9. Committer ensemble :
  ```batch
  git rm scripts/nom_du_script.py
  git add scripts/SCRIPTS_REFERENCE.py
  git commit -m "chore: remove nom_du_script - [raison]"
  ```

---

## ✅ Checklist pour SUPPRIMER un test

- [ ] 1. Ouvrir `scripts/SCRIPTS_REFERENCE.py`
- [ ] 2. Supprimer l'entrée dans `TESTS_CATALOG`
- [ ] 3. Ajouter une ligne dans le `CHANGELOG` : "Suppression de [nom] - [raison]"
- [ ] 4. Vérifier la liste : `python scripts\SCRIPTS_REFERENCE.py --list-tests`
- [ ] 5. Supprimer le fichier
- [ ] 6. Exécuter les tests restants : `run_all_tests.bat`
- [ ] 7. Committer ensemble :
  ```batch
  git rm tests/test_nom.py
  git add scripts/SCRIPTS_REFERENCE.py
  git commit -m "chore: remove test_nom - [raison]"
  ```

---

## ✅ Checklist AVANT CHAQUE COMMIT

Quelle que soit la modification :

- [ ] 1. Le venv est activé ou les .bat sont utilisés
- [ ] 2. `scripts/SCRIPTS_REFERENCE.py` est à jour
- [ ] 3. Le `CHANGELOG` dans SCRIPTS_REFERENCE.py contient l'entrée
- [ ] 4. Les tests passent : `run_all_tests.bat`
- [ ] 5. La liste est cohérente :
  ```batch
  python scripts\SCRIPTS_REFERENCE.py --list
  python scripts\SCRIPTS_REFERENCE.py --list-tests
  ```
- [ ] 6. Le commit inclut SCRIPTS_REFERENCE.py si nécessaire

---

## 🚫 ERREURS FRÉQUENTES À ÉVITER

### ❌ Oublier de mettre à jour SCRIPTS_REFERENCE.py
**Conséquence** : Le script/test n'est pas accessible via les .bat, pas documenté

**Solution** : Toujours inclure SCRIPTS_REFERENCE.py dans le commit

### ❌ Exécuter un test hors du venv
**Conséquence** : Incohérence des dépendances, résultats non fiables

**Solution** : Utiliser `run_test.bat` ou activer le venv

### ❌ Ne pas tester avant de committer
**Conséquence** : Code cassé dans le repo

**Solution** : Exécuter `run_all_tests.bat` avant chaque commit

### ❌ Oublier de mettre à jour last_modified
**Conséquence** : Impossible de tracer les modifications

**Solution** : Toujours mettre la date du jour

### ❌ Catégorie incorrecte
**Conséquence** : Difficile à retrouver dans les listes

**Solution** : Choisir la catégorie la plus appropriée

### ❌ Dépendances incomplètes
**Conséquence** : Erreur lors de l'exécution sur un autre environnement

**Solution** : Lister TOUS les imports (sauf stdlib)

---

## 📊 RÉSUMÉ RAPIDE

| Action | Fichiers à modifier | Commande de test |
|--------|-------------------|------------------|
| Ajouter script | script + SCRIPTS_REFERENCE.py | `run_script.bat nom` |
| Ajouter test | test + SCRIPTS_REFERENCE.py | `run_test.bat nom` + `run_all_tests.bat` |
| Modifier script | script + SCRIPTS_REFERENCE.py | `run_script.bat nom` |
| Modifier test | test + SCRIPTS_REFERENCE.py | `run_test.bat nom` + `run_all_tests.bat` |
| Supprimer script | SCRIPTS_REFERENCE.py | `run_all_tests.bat` |
| Supprimer test | SCRIPTS_REFERENCE.py | `run_all_tests.bat` |

---

## 📞 En cas de doute

1. Consulter `docs/MAINTENANCE_SCRIPTS_REFERENCE.md`
2. Consulter `README_SCRIPTS_SYSTEM.md`
3. Consulter `MEMO_VENV_USAGE.md`
4. Exécuter `python scripts\SCRIPTS_REFERENCE.py --help`

---

**IMPORTANT** : Imprimez cette checklist ou gardez-la ouverte lors de vos modifications !

**Dernière mise à jour** : 2025-11-10
