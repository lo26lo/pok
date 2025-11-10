# 🤖 Instructions GitHub Copilot - Projet Pokémon Dataset Generator

**Date de création** : 10 novembre 2025  
**Version** : 1.0

---

## 🎯 Règles Générales

### 1. Structure du Projet - NE JAMAIS MODIFIER SANS CONFIRMATION

**Racine propre obligatoire** :
- ✅ Seuls fichiers autorisés à la racine : `START.bat`, `INSTALL.bat`, `README.md`, `.gitignore`, `GUI_v3.1_modern.py`
- ❌ **JAMAIS** créer de nouveaux `.bat`, `.md`, `.py` à la racine
- ❌ **JAMAIS** déplacer des fichiers depuis `config/`, `models/`, `docs/`, `scripts/` vers la racine

**Organisation stricte** :
```
pok/
├── START.bat                    # Lanceur principal
├── INSTALL.bat                  # Installeur
├── README.md                    # Quick-start uniquement
├── GUI_v3.1_modern.py          # Application principale
│
├── config/                      # Configurations et requirements
├── models/                      # Modèles YOLO et mappings
├── docs/                        # TOUTE la documentation
├── scripts/                     # TOUS les scripts utilitaires
├── core/                        # Modules Python
├── tests/                       # Tests
└── [images/, output/, runs/]   # Données
```

---

## 🧪 Environnement Virtuel - RÈGLE ABSOLUE

### ⚠️ TOUS les tests doivent être exécutés dans le venv (.venv)

**Règle d'or** : **JAMAIS** exécuter un test ou script hors du venv

**✅ CORRECT** :
```batch
# Utiliser les fichiers .bat (méthode recommandée)
scripts\run_test.bat test_nom
scripts\run_script.bat nom_script

# OU activer le venv manuellement
call .venv\Scripts\activate.bat
python tests\test_nom.py
```

**❌ INCORRECT** :
```batch
# JAMAIS exécuter directement sans venv
python tests\test_nom.py          # ❌ Mauvais environnement
python scripts\init_prices.py     # ❌ Dépendances manquantes
```

**Pourquoi le venv est obligatoire** :
- ✅ Garantit les bonnes versions de dépendances (NumPy < 2.0, etc.)
- ✅ Isole l'environnement du projet
- ✅ Évite les conflits de packages
- ✅ Assure la reproductibilité des tests

**Vérifier le venv** :
```batch
python scripts\SCRIPTS_REFERENCE.py --check-venv
```

---

## 📝 Avant Toute Modification

### Checklist obligatoire :

1. **Lire la structure actuelle**
   - Vérifier où se trouvent les fichiers concernés
   - Respecter l'organisation `config/`, `models/`, `docs/`, `scripts/`

2. **Proposer d'abord, ne pas agir directement**
   - Expliquer ce qui sera fait
   - Attendre validation de l'utilisateur

3. **Documenter les changements** - ⚠️ RÈGLE ABSOLUE
   - **TOUJOURS** mettre à jour `README.md` (racine) si changement impacte utilisation
   - **TOUJOURS** mettre à jour `docs/README_COMPLET.md` si changement de fonctionnalité
   - Mettre à jour `docs/CHANGELOG.md` si modification majeure
   - Mettre à jour `scripts/SCRIPTS_REFERENCE.py` si ajout/modif de script/test
   - Mettre à jour les docs concernées dans `docs/` selon le type de changement

4. **Utiliser le venv pour les tests**
   - Toujours utiliser `scripts\run_test.bat` ou activer `.venv`
   - Vérifier que le venv existe avant de proposer des commandes

---

## 🔧 Règles Spécifiques par Type de Modification

### Ajout d'un nouveau script

**Emplacement** : `scripts/nom_du_script.py`

**Actions obligatoires** :
1. Créer le script dans `scripts/`
2. Mettre à jour `scripts/SCRIPTS_REFERENCE.py` :
   - Ajouter entrée dans `SCRIPTS_CATALOG`
   - Ajouter ligne dans `CHANGELOG`
   - Mettre à jour `last_modified`
3. Proposer test : `run_script.bat nom_du_script`
4. ❌ **NE JAMAIS** créer le script à la racine

### Ajout d'un nouveau test

**Emplacement** : `tests/test_nom.py`

**Actions obligatoires** :
1. Créer le test dans `tests/`
2. Mettre à jour `scripts/SCRIPTS_REFERENCE.py` :
   - Ajouter entrée dans `TESTS_CATALOG`
   - Ajouter ligne dans `CHANGELOG`
3. Proposer test : `run_test.bat test_nom`
4. ❌ **NE JAMAIS** créer le test à la racine

### Ajout de documentation

**Emplacement** : `docs/nom_du_document.md`

**Actions obligatoires** :
1. Créer dans `docs/`
2. Mettre à jour `README.md` (racine) si c'est une doc importante
3. Mettre à jour l'index dans `docs/README.md`
4. ❌ **NE JAMAIS** créer à la racine

### Modification de fonctionnalité

**Règle absolue** : Toute modification de fonctionnalité doit être documentée

**Actions obligatoires** :
1. **Mettre à jour `README.md` (racine)** :
   - Si changement visible par l'utilisateur
   - Si nouvelle fonctionnalité
   - Si modification de workflow
   - Si changement de commandes/scripts

2. **Mettre à jour `docs/README_COMPLET.md`** :
   - Si modification technique
   - Si changement d'architecture
   - Si ajout/suppression de dépendances
   - Si modification de configuration

3. **Mettre à jour `docs/CHANGELOG.md`** :
   - TOUJOURS pour toute modification de fonctionnalité
   - Respecter le format : `[Version] - Date - Description`

4. **Mettre à jour docs spécifiques** :
   - `docs/HELP.md` : Si impact sur l'utilisation
   - `docs/FEATURES.md` : Si nouvelle feature ou modification
   - `docs/DEPENDENCIES_MAP.md` : Si changement de dépendances
   - `scripts/SCRIPTS_REFERENCE.py` : Si ajout/modif script/test

**Exemples de modifications nécessitant mise à jour doc** :
- ✅ Ajout d'une feature GUI → README.md + README_COMPLET.md + FEATURES.md
- ✅ Modification d'un workflow → README.md + README_COMPLET.md
- ✅ Nouveau script → README_COMPLET.md + SCRIPTS_REFERENCE.py
- ✅ Changement de dépendance → README_COMPLET.md + DEPENDENCIES_MAP.md
- ✅ Nouvelle commande → README.md + README_COMPLET.md + HELP.md

### Modification de configuration

**Emplacements** :
- Fichiers config : `config/`
- Requirements : `config/requirements*.txt`
- API config : `config/api_config.json.example`

**Actions obligatoires** :
1. Modifier dans `config/`
2. ❌ **NE JAMAIS** créer de nouveaux fichiers config à la racine

### Ajout de modèles YOLO ou mappings

**Emplacement** : `models/`

**Fichiers concernés** :
- `models/yolo11n.pt`
- `models/yolov8n.pt`
- `models/card_name_to_id.json`

**Actions obligatoires** :
1. Placer dans `models/`
2. Mettre à jour les références dans le code si nécessaire
3. ❌ **NE JAMAIS** placer à la racine

---

## 🚨 Interdictions Formelles

### ❌ À NE JAMAIS FAIRE

1. **Créer des fichiers à la racine** (sauf `START.bat`, `INSTALL.bat`, `README.md`)
   - Pas de `.bat` supplémentaires
   - Pas de `.md` supplémentaires
   - Pas de `.py` supplémentaires
   - Pas de `.json`, `.txt`, `.yaml` supplémentaires

2. **Déplacer des fichiers vers la racine**
   - Tout doit rester dans `config/`, `models/`, `docs/`, `scripts/`

3. **Modifier la structure sans demander**
   - Toujours proposer avant d'agir

4. **Oublier de mettre à jour la documentation**
   - ❌ Modifier du code sans mettre à jour `README.md` si impact utilisateur
   - ❌ Ajouter une feature sans documenter dans `docs/README_COMPLET.md`
   - ❌ Changer un workflow sans mettre à jour les docs
   - ❌ Ajouter/modifier un script sans mettre à jour `SCRIPTS_REFERENCE.py`

5. **Oublier de mettre à jour `SCRIPTS_REFERENCE.py`**
   - Obligatoire pour tout script/test ajouté/modifié

6. **Créer de la documentation à la racine**
   - Toute doc va dans `docs/`

---

## ✅ Workflow de Validation

Avant chaque commit proposé :

```batch
# 1. Vérifier que la racine est propre
# Seuls fichiers autorisés : START.bat, INSTALL.bat, README.md, .gitignore, GUI_v3.1_modern.py

# 2. Vérifier que les fichiers sont aux bons endroits
# config/ → configurations
# models/ → modèles et mappings
# docs/ → documentation
# scripts/ → scripts utilitaires

# 3. Vérifier SCRIPTS_REFERENCE.py si ajout/modif script/test

# 4. Proposer le commit avec message clair
```

---

## 📚 Documentation à Consulter

Avant toute action complexe, consulter :

1. **`docs/README_COMPLET.md`** - Documentation complète du projet
2. **`docs/CHANGELOG.md`** - Historique des modifications
3. **`docs/DEPENDENCIES_MAP.md`** - Qui appelle quoi
4. **`docs/README_SCRIPTS_SYSTEM.md`** - Système centralisé de scripts
5. **`docs/CHECKLIST_MODIFICATIONS.md`** - Checklist pour modifications

---

## 🎯 Phrases Clés de l'Utilisateur

### "je veux créer un nouveau script"
→ Réponse : "Je vais créer `scripts/nom_du_script.py` et mettre à jour `scripts/SCRIPTS_REFERENCE.py`. Confirmes-tu ?"

### "j'ai besoin d'une nouvelle doc"
→ Réponse : "Je vais créer `docs/nom_du_document.md`. Confirmes-tu ?"

### "ajoute ce fichier"
→ Réponse : "Où dois-je placer ce fichier ? (`config/`, `models/`, `docs/`, `scripts/`) pour respecter la structure du projet."

### Toute demande de création à la racine
→ Réponse : "⚠️ La racine doit rester propre. Je propose de placer ce fichier dans `[dossier approprié]/`. Confirmes-tu ?"

---

## 🔄 Mise à Jour de ce Fichier

Ce fichier doit être mis à jour lors de :
- Changements de structure majeurs
- Ajout de nouvelles règles
- Retours d'expérience de l'utilisateur

**Dernière mise à jour** : 10 novembre 2025  
**Par** : Utilisateur + GitHub Copilot

---

## 💡 Rappels Importants

> **"À la racine on ne devrait avoir que le bat de lancement et le readme"**  
> — Utilisateur, 10 novembre 2025

Cette règle est **ABSOLUE** et doit être respectée en toutes circonstances.

**Racine propre = Projet professionnel** ✨
