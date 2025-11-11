# 🤖 Instructions GitHub Copilot - Projet Pokémon Dataset Generator

**Date de création** : 10 novembre 2025  
**Dernière mise à jour** : 11 novembre 2025  
**Version** : 2.1

> **ℹ️ Note** : Ce fichier contient les instructions **détaillées** pour GitHub Copilot.  
> Pour un résumé rapide destiné à tous les agents IA, consultez `.agent.md` à la racine.

---

## 🎯 Règles Générales

### 0. Workflow de Planification - NOUVEAU SYSTÈME

**Pour toute nouvelle fonctionnalité ou modification majeure** :

#### 📋 Créer un document de planification

**Emplacement** : `.planning/YYYY-MM-DD_description-courte.md`  
**Template** : Utiliser `.planning/TEMPLATE.md`

**Quand créer un document de planification ?**
- ✅ Nouvelle fonctionnalité demandée
- ✅ Modification majeure d'architecture
- ✅ Refactorisation importante
- ✅ Ajout de plusieurs scripts/tests
- ❌ Simple bug fix (sauf si complexe)
- ❌ Modification mineure de documentation

**Structure obligatoire du document** :
1. **Vue d'ensemble** : Description, objectif, impact
2. **Planification par étapes** : Étapes détaillées avec actions et validations
3. **Suivi des progrès** : Timeline, progression, journal des modifications
4. **Questions de clarification** : Questions ouvertes, décisions prises, points d'attention
5. **Détails techniques** : Dépendances, modifications, tests
6. **Documentation à mettre à jour** : Liste des docs concernées
7. **Checklist finale** : Validation avant commit

**Workflow type** :
```
1. Utilisateur fait une demande
2. ⚠️ AVANT TOUT CODE : Créer document de planification
3. Proposer les étapes à l'utilisateur
4. Obtenir validation/clarifications
5. Exécuter étape par étape
6. Mettre à jour progression dans le document
7. Finaliser (tests + docs)
8. Checklist finale avant commit
```

**Mise à jour du document** :
- ✅ Mettre à jour après chaque étape terminée
- ✅ Ajouter questions au fur et à mesure
- ✅ Logger toutes les décisions importantes
- ✅ Marquer progrès dans la timeline

**Nommage des fichiers** :
- Format : `YYYY-MM-DD_description-courte.md`
- Exemples :
  - `2025-11-11_systeme-planification.md`
  - `2025-11-11_nouveau-workflow-augmentation.md`
  - `2025-11-11_integration-api-pokemon.md`

**Ce dossier est gitignored** : Les documents de planification sont des work-in-progress et ne doivent pas être versionnés.

---

### 1. Structure du Projet - NE JAMAIS MODIFIER SANS CONFIRMATION

**Racine propre obligatoire** :
- ✅ Seuls fichiers autorisés à la racine : `START.bat`, `INSTALL.bat`, `README.md`, `.gitignore`, `.agent.md`, `GUI_v3.1_modern.py`
- ❌ **JAMAIS** créer de nouveaux `.bat`, `.md`, `.py` à la racine (sauf `.agent.md` pour instructions IA)
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

## ⚙️ Contraintes Techniques

### Python
- **Version recommandée** : Python 3.12
- **Versions supportées** : 3.10, 3.11, 3.12
- **Versions interdites** : 3.13+ (problèmes de compatibilité NumPy 1.x)

### Dépendances critiques
- **NumPy** : `< 2.0` (OBLIGATOIRE pour imgaug)
- **OpenCV** : `< 4.10.0` (compatibilité NumPy 1.x)
- **imgaug** : `>= 0.4.0` (nécessite NumPy < 2.0)
- **scipy** : `< 1.14`
- **scikit-image** : `< 0.23`

### GPU & CUDA
- **PyTorch** : Installation selon GPU :
  - RTX 40xx/50xx → CUDA 12.4
  - RTX 30xx → CUDA 11.8
  - CPU uniquement → version CPU
- **Ultralytics** : Détection auto du GPU

### Encodage & Unicode
- **Toujours** UTF-8 pour les fichiers
- **Utiliser** `safe_print()` pour les logs (gère ASCII/Unicode)
- **Windows** : `PYTHONIOENCODING=utf-8` dans START.bat

### Limitations connues
- imgaug ne supporte pas NumPy 2.0+
- Certaines augmentations sont lentes sur CPU
- Mosaïques : max 8 cartes par layout (performance)

---

## 🎨 Standards de Code Python

### Style général
- **PEP 8** pour la mise en forme de base
- **Type hints** encouragés pour les fonctions publiques
- **Docstrings** pour les fonctions complexes (format Google ou NumPy)
- **Imports** : stdlib → third-party → local (séparés par ligne vide)

### Gestion des erreurs
- Utiliser `try/except` avec des exceptions spécifiques
- Logger les erreurs avec le module `logging`
- Ne jamais utiliser `except:` sans type d'exception
- Préférer `safe_print()` de `core/utils.py` pour l'affichage console

### Fonctions utilitaires
- **TOUJOURS** utiliser les fonctions de `core/utils.py` :
  - `safe_print()` : Affichage console (gère Unicode)
  - `ensure_dir()` : Création de dossiers
  - `validate_path()` : Validation de chemins
  
### Chemins de fichiers
- **TOUJOURS** utiliser `pathlib.Path` ou `os.path.join`
- **JAMAIS** de chemins en dur avec `\` ou `/`
- Préférer les chemins relatifs depuis la racine du projet

### Exemple de fonction bien structurée
```python
from pathlib import Path
from typing import Optional, List
import logging

from core.utils import safe_print, ensure_dir

def process_images(
    input_dir: Path,
    output_dir: Path,
    count: int = 10
) -> Optional[List[str]]:
    """
    Traite les images d'un dossier.
    
    Args:
        input_dir: Dossier source
        output_dir: Dossier destination
        count: Nombre d'images à traiter
        
    Returns:
        Liste des fichiers traités ou None si erreur
    """
    try:
        ensure_dir(output_dir)
        processed = []
        
        # Logique ici
        
        safe_print(f"✅ {len(processed)} images traitées")
        return processed
        
    except FileNotFoundError as e:
        logging.error(f"Dossier introuvable : {e}")
        return None
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")
        return None
```

---

## 🔤 Conventions de Nommage

### Fichiers Python
- **Scripts** : `snake_case.py` (ex: `init_prices.py`)
- **Tests** : `test_<nom>.py` (ex: `test_cuda.py`)
- **Modules** : `snake_case.py` (ex: `card_mapping.py`)

### Fichiers Batch
- **Lanceurs** : `MAJUSCULES.bat` (ex: `START.bat`, `INSTALL.bat`)
- **Utilitaires** : `snake_case.bat` (ex: `run_test.bat`)

### Fichiers Documentation
- **README** : `README_DESCRIPTIF.md` (ex: `README_COMPLET.md`)
- **Autres docs** : `MAJUSCULES.md` (ex: `CHANGELOG.md`, `HELP.md`)

### Code Python
- **Variables** : `snake_case` (ex: `image_count`, `output_dir`)
- **Constantes** : `UPPER_SNAKE_CASE` (ex: `MAX_CARDS`, `DEFAULT_EPOCHS`)
- **Fonctions** : `snake_case` (ex: `download_images()`, `create_mosaic()`)
- **Classes** : `PascalCase` (ex: `ImageDownloader`, `MosaicGenerator`)
- **Privé** : préfixe `_` (ex: `_internal_method()`)

### Noms de dossiers
- **Données** : `lowercase` (ex: `images/`, `output/`, `runs/`)
- **Code** : `lowercase` (ex: `core/`, `tests/`, `scripts/`)
- **Config** : `lowercase` (ex: `config/`, `models/`)

### Noms de variables GUI (tkinter)
- **Widgets** : `type_description` (ex: `btn_start`, `lbl_status`, `entry_epochs`)
- **Variables** : `var_description` (ex: `var_model_size`, `var_batch_size`)

### Exemples à suivre
```python
# ✅ BON
def create_card_mapping(input_dir: Path, output_file: Path) -> bool:
    MAX_RETRIES = 3
    card_count = 0
    mapping_dict = {}
    
    for attempt in range(MAX_RETRIES):
        # ...
    
    return True

# ❌ MAUVAIS
def CreateCardMapping(InputDir, OutputFile):  # PascalCase pour fonction
    maxRetries = 3  # camelCase pour constante
    CardCount = 0  # PascalCase pour variable
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

## 💬 Messages de Commit

### Format obligatoire
```
<type>(<scope>): <description courte>

<description détaillée optionnelle>
```

### Types autorisés
- **feat** : Nouvelle fonctionnalité
- **fix** : Correction de bug
- **docs** : Documentation uniquement
- **style** : Formatage, pas de changement de code
- **refactor** : Refactorisation sans changement de comportement
- **test** : Ajout/modification de tests
- **chore** : Maintenance (dépendances, config)
- **perf** : Amélioration de performance

### Scopes courants
- **gui** : Interface graphique
- **core** : Modules core/
- **scripts** : Scripts utilitaires
- **tests** : Tests
- **docs** : Documentation
- **config** : Configuration

### Exemples de bons messages
```bash
✅ feat(gui): add holographic intensity slider
✅ fix(core): resolve NumPy 2.0 compatibility issue
✅ docs: update README with new workflow diagram
✅ refactor(scripts): centralize SCRIPTS_REFERENCE.py
✅ test: add GPU detection test
✅ chore(config): pin NumPy to < 2.0
```

### Exemples de mauvais messages
```bash
❌ update files
❌ fix bug
❌ wip
❌ changes
```

### Règles
- **Impératif** : "add" pas "added" ou "adds"
- **Minuscule** : pas de majuscule après le type
- **Pas de point** à la fin
- **50 caractères max** pour la description courte
- **Corps de 72 caractères** par ligne si ajouté

---

## 🧪 Tests & Validation

### Quand tester ?

**TOUJOURS tester avant commit si modification de** :
- ✅ `core/` : Modules principaux → `run_all_tests.bat`
- ✅ `scripts/` : Scripts → `run_script.bat <nom>`
- ✅ Configuration : Dependencies → `test_project_integrity`
- ✅ GUI : Interface → Lancer `START.bat` et tester manuellement

### Tests automatiques disponibles

**Hardware** :
```batch
scripts\run_test.bat test_cuda  # Test GPU/CUDA
```

**Intégrité** :
```batch
scripts\run_test.bat test_project_integrity  # Structure complète
```

**Performance** :
```batch
scripts\run_test.bat test_mosaic_performance  # Benchmark mosaics
scripts\run_test.bat test_holographic_performance  # Benchmark holo
```

**Validation** :
```batch
scripts\run_test.bat verify_data_yaml  # Vérifier dataset YOLO
scripts\run_test.bat check_corrupted_images  # Images corrompues
```

### Workflow de test recommandé

**Avant commit** :
```batch
# 1. Tests d'intégrité
scripts\run_test.bat test_project_integrity

# 2. Tests spécifiques selon modif
scripts\run_test.bat <test_concerné>

# 3. Vérification manuelle GUI si nécessaire
START.bat
```

**Après modification majeure** :
```batch
# Tous les tests
scripts\run_all_tests.bat
```

### Créer un nouveau test

**Structure recommandée** :
```python
# tests/test_ma_feature.py
import pytest
from pathlib import Path
import sys

# Ajouter core/ au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ma_feature import ma_fonction

def test_ma_fonction_basic():
    """Test basique de ma_fonction"""
    result = ma_fonction(input_data)
    assert result is not None
    assert len(result) > 0

def test_ma_fonction_edge_case():
    """Test cas limite"""
    result = ma_fonction(None)
    assert result == []

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Puis ajouter à `scripts/SCRIPTS_REFERENCE.py`** !

---

## 🔄 Workflows Types

### Workflow 1 : Ajouter une nouvelle fonctionnalité GUI

**Étapes** :
1. **Modifier** `GUI_v3.1_modern.py`
2. **Tester** : Lancer `START.bat` et vérifier
3. **Documenter** :
   - Mettre à jour `README.md` (section Features)
   - Mettre à jour `docs/README_COMPLET.md` (section GUI)
   - Mettre à jour `docs/FEATURES.md`
   - Ajouter dans `docs/CHANGELOG.md`
4. **Commit** : `feat(gui): add <description>`

### Workflow 2 : Ajouter un nouveau script

**Étapes** :
1. **Créer** `scripts/mon_script.py`
2. **Mettre à jour** `scripts/SCRIPTS_REFERENCE.py` :
   - Ajouter dans `SCRIPTS_CATALOG`
   - Ajouter ligne dans `CHANGELOG`
3. **Tester** : `scripts\run_script.bat mon_script`
4. **Documenter** :
   - Mettre à jour `docs/README_COMPLET.md` (section Scripts)
   - Ajouter dans `docs/CHANGELOG.md`
5. **Commit ensemble** : script + SCRIPTS_REFERENCE.py + docs

### Workflow 3 : Corriger un bug

**Étapes** :
1. **Identifier** le bug (fichier, ligne, symptôme)
2. **Créer un test** qui reproduit le bug (si possible)
3. **Corriger** le code
4. **Vérifier** que le test passe maintenant
5. **Tester** les cas connexes
6. **Documenter** si bug affecte utilisateurs :
   - Ajouter dans `docs/CHANGELOG.md`
   - Mettre à jour doc concernée si nécessaire
7. **Commit** : `fix(<scope>): <description>`

### Workflow 4 : Modifier une dépendance

**Étapes** :
1. **Modifier** `config/requirements.txt`
2. **Tester** la compatibilité :
   ```batch
   rmdir /s /q .venv
   INSTALL.bat
   scripts\run_all_tests.bat
   ```
3. **Documenter** :
   - Mettre à jour `docs/README_COMPLET.md` (section Dependencies)
   - Mettre à jour `docs/DEPENDENCIES_MAP.md`
   - Ajouter dans `docs/CHANGELOG.md`
4. **Commit** : `chore(config): update <package> to version X`

### Workflow 5 : Refactoriser du code

**Étapes** :
1. **S'assurer** que les tests passent AVANT
2. **Refactoriser** le code
3. **Vérifier** que les tests passent APRÈS (même comportement)
4. **Documenter** si changement d'API :
   - Mettre à jour `docs/DEPENDENCIES_MAP.md`
   - Mettre à jour docs techniques
5. **Commit** : `refactor(<scope>): <description>`

---

## � Système de Planification par Étapes

### Quand créer un document de planification ?

**✅ OBLIGATOIRE pour** :
- Nouvelle fonctionnalité majeure
- Refactorisation d'architecture
- Ajout de plusieurs scripts/modules interconnectés
- Modifications impactant plusieurs composants
- Intégration d'API externe
- Modification du workflow utilisateur

**❌ NON NÉCESSAIRE pour** :
- Simple bug fix ponctuel
- Correction de typo
- Mise à jour mineure de documentation
- Ajout d'un seul petit script

### Processus de création

**1. Dès qu'une demande majeure arrive** :
```
⚠️ AVANT TOUT CODE : Créer le document de planification
```

**2. Créer le fichier** :
```
.planning/YYYY-MM-DD_description-courte.md
```

**3. Utiliser le template** :
- Copier depuis `.planning/TEMPLATE.md`
- Remplir les sections obligatoires

**4. Proposer à l'utilisateur** :
- Présenter les étapes prévues
- Demander validation/clarifications
- Ajuster selon feedback

**5. Exécuter étape par étape** :
- Marquer chaque étape en "En cours" avant de commencer
- Effectuer les actions
- Mettre à jour la progression
- Marquer "Terminé" une fois validé

**6. Tenir à jour** :
- Ajouter questions au fur et à mesure
- Logger les décisions importantes
- Mettre à jour la timeline
- Noter les blocages rencontrés

**7. Finaliser** :
- Cocher la checklist finale
- S'assurer que toute la doc est à jour
- Préparer le message de commit

### Structure du document

**Sections obligatoires** :

1. **🎯 Vue d'ensemble**
   - Description de la demande originale
   - Objectif clair et mesurable
   - Impact attendu (utilisateur, technique, doc)

2. **📝 Planification par étapes**
   - Étapes numérotées et titrées
   - Actions concrètes (checklist)
   - Fichiers concernés par étape
   - Critères de validation

3. **📊 Suivi des progrès**
   - Timeline visuelle
   - Pourcentage d'avancement
   - Journal des modifications avec dates
   - Temps estimé restant

4. **❓ Questions de clarification**
   - Questions ouvertes avec contexte
   - Décisions prises (avec date)
   - Points d'attention/risques

5. **🔧 Détails techniques**
   - Dépendances nécessaires
   - Modifications de structure prévues
   - Tests à effectuer
   - Contraintes de compatibilité

6. **📚 Documentation à mettre à jour**
   - Liste des fichiers doc concernés
   - Sections précises à modifier

7. **✅ Checklist finale**
   - Validation avant commit
   - Points de non-régression

### Exemple de nommage

```
.planning/2025-11-11_systeme-planification.md
.planning/2025-11-15_integration-tcgdex-api.md
.planning/2025-11-20_refonte-module-augmentation.md
.planning/2025-12-01_support-multi-gpu.md
```

### Workflow visuel

```
Demande utilisateur
      ↓
⚠️ Créer document .planning/
      ↓
Remplir vue d'ensemble + étapes
      ↓
→ Proposer à l'utilisateur ←
      ↓                    ↑
Obtenir validation?    NON ┘
      ↓ OUI
Pour chaque étape:
  - Marquer "En cours"
  - Exécuter actions
  - Mettre à jour progrès
  - Logger décisions
  - Marquer "Terminé"
      ↓
Checklist finale
      ↓
Commit avec docs à jour
```

### Mise à jour continue

**Après chaque étape terminée** :
```markdown
### Journal des modifications
| Date | Étape | Action | Résultat |
|------|-------|--------|----------|
| 2025-11-11 | Étape 1 | Création fichier X | ✅ |
| 2025-11-11 | Étape 2 | Tests intégration | ⚠️ Ajustement nécessaire |
```

**Quand une question surgit** :
```markdown
### Questions ouvertes
1. **Faut-il supporter Python 3.9 ?**
   - Contexte : NumPy < 2.0 supporté sur 3.9
   - Options : A) Oui, B) Non (3.10+ seulement)
   - Recommandation : B car simplification dépendances
   - ⏳ En attente de réponse utilisateur
```

**Quand une décision est prise** :
```markdown
| Date | Question | Décision | Justification |
|------|----------|----------|---------------|
| 2025-11-11 | Support Python 3.9 | Non | Simplification maintenance |
```

### Exemple concret

Utilisateur : "Je veux intégrer l'API TCGdex pour récupérer les prix"

**Copilot crée** : `.planning/2025-11-11_integration-api-tcgdex.md`

**Contenu** :
```markdown
# 📋 Planification : Intégration API TCGdex pour récupération prix

## 🎯 Vue d'ensemble
Intégrer l'API TCGdex pour récupérer automatiquement les prix des cartes...

## 📝 Planification par étapes

### Étape 1 : Création module API
**Statut** : 🔄 En cours
**Actions** :
- [x] Créer core/tcgdex_api.py
- [x] Implémenter get_card_price()
- [ ] Ajouter gestion cache
...

## 📊 Suivi des progrès
**Avancement** : 2 / 5 étapes (40%)

## ❓ Questions de clarification
1. **Fréquence de refresh des prix ?**
   - ⏳ En attente
...
```

**Copilot propose** : "J'ai préparé un plan en 5 étapes. Veux-tu que je commence ?"

**Utilisateur valide** → Copilot exécute étape par étape en mettant à jour le document

### Avantages du système

✅ **Traçabilité** : Historique complet des décisions  
✅ **Communication** : Utilisateur voit le plan avant exécution  
✅ **Clarifications** : Questions documentées  
✅ **Progrès** : Suivi visuel de l'avancement  
✅ **Documentation** : Base pour CHANGELOG et docs  
✅ **Reproductibilité** : Plan peut être réutilisé

---

## �🚨 Debugging & Troubleshooting

### Problèmes courants et solutions

#### 1. "ModuleNotFoundError"
**Cause** : venv pas activé ou dépendances manquantes
**Solution** :
```batch
call .venv\Scripts\activate.bat
pip install -r config/requirements.txt
```

#### 2. "NumPy 2.0 incompatible"
**Cause** : NumPy 2.0+ installé (incompatible imgaug)
**Solution** :
```batch
pip uninstall numpy
pip install "numpy<2.0"
```

#### 3. "UnicodeEncodeError" dans logs
**Cause** : Caractères spéciaux sur Windows
**Solution** : Utiliser `safe_print()` de `core/utils.py`

#### 4. GPU pas détecté
**Cause** : PyTorch CPU installé ou drivers NVIDIA manquants
**Solution** :
```batch
# Vérifier
python -c "import torch; print(torch.cuda.is_available())"

# Réinstaller PyTorch GPU
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

#### 5. Tests échouent sans raison
**Cause** : Tests exécutés hors venv
**Solution** : TOUJOURS utiliser `scripts\run_test.bat`

### Outils de debug

**Logs détaillés** :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Profiling** :
```python
import cProfile
cProfile.run('ma_fonction()')
```

**Vérifier environnement** :
```batch
python scripts\SCRIPTS_REFERENCE.py --check-venv
scripts\run_test.bat test_project_integrity
```

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

**Historique des versions** :
- **v2.1** (11 novembre 2025) : Ajout système de planification par étapes (.planning/)
- **v2.0** (10 novembre 2025) : Ajout de 7 sections complètes (Contraintes Techniques, Standards de Code, Conventions de Nommage, Messages de Commit, Tests & Validation, Workflows Types, Debugging & Troubleshooting)
- **v1.0** (10 novembre 2025) : Version initiale

**Dernière mise à jour** : 11 novembre 2025  
**Par** : Utilisateur + GitHub Copilot

---

## 💡 Rappels Importants

> **"À la racine on ne devrait avoir que le bat de lancement et le readme"**  
> — Utilisateur, 10 novembre 2025

Cette règle est **ABSOLUE** et doit être respectée en toutes circonstances.

**Racine propre = Projet professionnel** ✨
