# 🗺️ AJOUT DE LA CARTOGRAPHIE DES DÉPENDANCES

## 📅 Date : 2025-11-10

## 🎯 Objectif

Compléter le système centralisé en ajoutant **la cartographie complète des dépendances** pour répondre à la question : **"Qui appelle quoi ?"**

---

## ✅ Ce qui a été ajouté

### 1. **DEPENDENCIES_MAP.md** (Nouveau fichier - 650+ lignes)

Cartographie textuelle détaillée contenant :

#### 📋 Sections principales :

1. **GUI → Modules Core**
   - Liste tous les imports directs du GUI
   - Appels de fonctionnalités par onglet
   - Appels via subprocess

2. **Modules Core → Autres Modules**
   - workflow_manager : Appelle augmentation, holographic, mosaic, auto_balancer, dataset_exporter
   - training_manager : Appelle YOLO
   - detection_manager : Appelle YOLO, cv2
   - detection_with_prices : Appelle utils, card_mapping
   - image_downloader : Appelle tcgdex_api
   - etc.

3. **Scripts → Modules Core**
   - init_prices.py : Utilise pandas, yaml
   - create_card_mapping.py : Utilise yaml
   - workflow_optimized.py : Utilise workflow_manager
   - etc.

4. **Tests → Modules Core**
   - test_cuda.py : Teste torch
   - test_detection_prices.py : Teste detection_with_prices
   - test_workflow_simulation.py : Teste tcgdex_api
   - etc.

5. **Workflows Complets**
   - Workflow 1 : Téléchargement → Entraînement (diagramme textuel)
   - Workflow 2 : Détection avec Prix (diagramme textuel)
   - Workflow 3 : Génération de Backgrounds

6. **Matrice de Dépendances**
   - Tableau complet : Composant | Dépend de | Appelé par

7. **Dépendances Externes**
   - ultralytics, opencv-python, torch, pandas, requests, PyYAML, tkinter, openpyxl

8. **Points d'Attention**
   - Dépendances circulaires (aucune détectée)
   - Couplage fort (GUI ↔ Core Managers)
   - Appels subprocess (risques)

9. **Règles de Maintenance**
   - Checklist lors de l'ajout d'une dépendance
   - Checklist lors de modification d'interface
   - Checklist lors de refactorisation

10. **Comment Tracer une Dépendance**
    - Exemples pratiques de recherche

11. **Graphe ASCII**
    - Visualisation ASCII de l'architecture

---

### 2. **docs/DEPENDENCY_GRAPH.md** (Nouveau fichier - 450+ lignes)

Diagrammes visuels interactifs avec **Mermaid** :

#### 📊 Diagrammes inclus :

1. **Architecture Complète**
   ```mermaid
   graph TB
       GUI --> workflow_manager
       GUI --> training_manager
       GUI --> detection_manager
       workflow_manager --> augmentation
       workflow_manager --> holographic_augmenter
       etc.
   ```

2. **Workflow Téléchargement → Entraînement**
   - Flowchart détaillé du processus complet

3. **Workflow Détection avec Prix**
   - Flowchart de la détection en temps réel

4. **Architecture des Tests**
   - Graph montrant run_all_tests.bat → SCRIPTS_REFERENCE.py → 16 tests

5. **Modules Core - Interdépendances**
   - Graph montrant les relations entre modules core

6. **Scripts Principaux - Appels**
   - Graph montrant qui appelle quels scripts

7. **Dépendances Externes**
   - Graph montrant les packages Python utilisés

#### 🎨 Fonctionnalités :

- Affichage automatique sur GitHub/GitLab
- Extension VS Code : Markdown Preview Mermaid Support
- Export vers images : mermaid-cli
- Éditeur en ligne : mermaid.live

---

### 3. **scripts/SCRIPTS_REFERENCE.py** (Modifié)

Ajout du champ **`"called_by"`** dans tous les catalogues :

#### SCRIPTS_CATALOG :

```python
"init_prices": {
    "path": SCRIPTS_DIR / "init_prices.py",
    "description": "Initialise les prix des cartes depuis data.yaml vers Excel",
    "category": "Configuration",
    "dependencies": ["pandas", "openpyxl", "PyYAML"],
    "arguments": [],
    "requires_venv": True,
    "called_by": ["Utilisateur (manuel)", "workflow après téléchargement images"],  # ← NOUVEAU
    "last_modified": "2025-11-10"
}
```

#### TESTS_CATALOG :

```python
"test_cuda": {
    "path": TESTS_DIR / "test_cuda.py",
    "description": "Teste la disponibilité CUDA/GPU",
    "category": "Hardware",
    "dependencies": ["torch"],
    "requires_venv": True,
    "called_by": ["run_test.bat", "run_all_tests.bat", "test_pytorch_gpu.bat"],  # ← NOUVEAU
    "last_modified": "2025-11-10"
}
```

#### Affichage mis à jour :

```
▶️  Exécution: .venv\Scripts\python.exe scripts\init_prices.py
📝 Description: Initialise les prix des cartes depuis data.yaml vers Excel
📦 Dépendances: pandas, openpyxl, PyYAML
🔗 Appelé par: Utilisateur (manuel), workflow après téléchargement images  # ← NOUVEAU
```

---

### 4. **README_SCRIPTS_SYSTEM.md** (Modifié)

Ajout d'un tableau de **documentation complète** :

```markdown
## 📚 Documentation Complète

| Fichier | Description |
|---------|-------------|
| **README_SCRIPTS_SYSTEM.md** (ce fichier) | Guide d'utilisation principal |
| **DEPENDENCIES_MAP.md** | Cartographie complète : Qui appelle quoi ? |  # ← NOUVEAU
| **docs/DEPENDENCY_GRAPH.md** | Diagrammes visuels interactifs (Mermaid) |  # ← NOUVEAU
| **docs/MAINTENANCE_SCRIPTS_REFERENCE.md** | Guide de maintenance détaillé |
| **MEMO_VENV_USAGE.md** | Mémo rapide pour l'usage quotidien |
| **CHECKLIST_MODIFICATIONS.md** | Checklist lors de modifications |
```

---

### 5. **SYSTEME_CENTRALISE_VISUAL.txt** (Modifié)

Mise à jour de la section "FICHIERS PRINCIPAUX" :

```
scripts/SCRIPTS_REFERENCE.py  ← 🔥 CATALOGUE CENTRALISÉ (À MAINTENIR!)
       │
       ├─→ SCRIPTS_CATALOG (14 scripts avec "called_by")  # ← MAJ
       ├─→ TESTS_CATALOG (16 tests avec "called_by")       # ← MAJ
       └─→ Interface CLI complète

DEPENDENCIES_MAP.md          ← 🗺️ CARTOGRAPHIE DES DÉPENDANCES  # ← NOUVEAU
       │
       ├─→ GUI → Core Modules
       ├─→ Modules Core → Autres Modules
       ├─→ Scripts → Modules Core
       ├─→ Tests → Modules Core
       ├─→ Workflows complets
       └─→ Matrice de dépendances

docs/DEPENDENCY_GRAPH.md     ← 📊 DIAGRAMMES VISUELS (Mermaid)  # ← NOUVEAU
       │
       ├─→ Architecture complète
       ├─→ Workflow téléchargement → entraînement
       ├─→ Workflow détection avec prix
       ├─→ Architecture des tests
       ├─→ Modules core interdépendances
       └─→ Dépendances externes
```

---

## 📊 Résumé des Modifications

| Fichier | Type | Lignes | Changements |
|---------|------|--------|-------------|
| **DEPENDENCIES_MAP.md** | Nouveau | 650+ | Cartographie textuelle complète |
| **docs/DEPENDENCY_GRAPH.md** | Nouveau | 450+ | Diagrammes Mermaid interactifs |
| **scripts/SCRIPTS_REFERENCE.py** | Modifié | +28 | Ajout champ "called_by" (14 scripts + 16 tests) |
| **README_SCRIPTS_SYSTEM.md** | Modifié | +10 | Ajout tableau documentation |
| **SYSTEME_CENTRALISE_VISUAL.txt** | Modifié | +25 | Mise à jour section fichiers principaux |
| **RECAPITULATIF_DEPENDENCIES.md** | Nouveau | 250+ | Ce fichier (résumé des ajouts) |

**Total : 6 fichiers modifiés/créés**

---

## 🎯 Cas d'Usage

### 1. Comprendre les dépendances d'un script

**Question** : "Qui appelle `init_prices.py` ?"

**Réponse dans SCRIPTS_REFERENCE.py** :
```python
"called_by": ["Utilisateur (manuel)", "workflow après téléchargement images"]
```

**Détails dans DEPENDENCIES_MAP.md** :
- Section "Scripts → Modules Core"
- Workflow 1 : Téléchargement → Entraînement

---

### 2. Visualiser l'architecture complète

**Fichier** : `docs/DEPENDENCY_GRAPH.md`

**Diagramme** : "Architecture Complète"

**Résultat** : Graph montrant toutes les relations entre GUI, managers, modules core, et packages externes.

---

### 3. Tracer l'impact d'une modification

**Scénario** : Je modifie `core/card_mapping.py`

**Étapes** :

1. **Consulter DEPENDENCIES_MAP.md** → Section "Modules Core → Autres Modules"
   ```
   core/card_mapping.py
       └── Appelé par: detection_with_prices.py
   ```

2. **Remonter la chaîne** :
   ```
   detection_with_prices.py
       └── Appelé par: detection_manager.py
           └── Appelé par: GUI_v3.1_modern.py (Detection tab)
   ```

3. **Tests à exécuter** :
   ```
   test_detection_prices.py
   test_mapping_debug.py
   ```

**Conclusion** : Modifier `card_mapping.py` impacte la détection avec prix dans le GUI.

---

### 4. Identifier les dépendances externes

**Question** : "Quels modules utilisent OpenCV ?"

**Réponse dans DEPENDENCIES_MAP.md** → Section "Dépendances Externes" :
- augmentation.py
- holographic_augmenter.py
- mosaic.py
- detection_manager.py
- detection_with_prices.py
- random_erasing.py

**Visualisation** : `docs/DEPENDENCY_GRAPH.md` → Diagramme "Dépendances Externes"

---

## 🔄 Workflow de Maintenance

### Lors de l'ajout d'une nouvelle dépendance :

1. ✅ **Mettre à jour SCRIPTS_REFERENCE.py**
   - Ajouter dans SCRIPTS_CATALOG ou TESTS_CATALOG
   - Renseigner le champ "called_by"

2. ✅ **Mettre à jour DEPENDENCIES_MAP.md**
   - Section correspondante (GUI → Core, Scripts → Core, etc.)
   - Matrice de dépendances
   - Workflows si nécessaire

3. ✅ **Mettre à jour docs/DEPENDENCY_GRAPH.md**
   - Ajouter dans les diagrammes Mermaid

4. ✅ **Tester** :
   ```batch
   run_all_tests.bat
   ```

---

## 🎨 Fonctionnalités Visuelles

### Diagrammes Mermaid

**Avantages** :
- ✅ Affichage automatique sur GitHub/GitLab
- ✅ Modification facile (code text)
- ✅ Versionnable avec Git
- ✅ Export vers images (PNG, SVG, PDF)

**Outils** :
- Extension VS Code : `bierner.markdown-mermaid`
- En ligne : https://mermaid.live/
- CLI : `npm install -g @mermaid-js/mermaid-cli`

**Exemple de génération d'image** :
```bash
mmdc -i docs/DEPENDENCY_GRAPH.md -o dependency_graph.png
```

---

## 📝 Checklist de Vérification

Avant de committer :

- [ ] SCRIPTS_REFERENCE.py mis à jour avec "called_by"
- [ ] DEPENDENCIES_MAP.md contient toutes les nouvelles dépendances
- [ ] docs/DEPENDENCY_GRAPH.md mis à jour si modification d'architecture
- [ ] README_SCRIPTS_SYSTEM.md cohérent
- [ ] SYSTEME_CENTRALISE_VISUAL.txt cohérent
- [ ] Tests exécutés avec succès (`run_all_tests.bat`)
- [ ] CHANGELOG.md mis à jour

---

## 🚀 Prochaines Étapes Recommandées

### 1. Automatisation

Créer un script qui :
- Parse automatiquement les imports Python
- Génère DEPENDENCIES_MAP.md
- Génère les diagrammes Mermaid
- Détecte les dépendances circulaires

### 2. Analyse de dépendances

Créer un outil qui :
- Analyse l'impact d'une modification
- Liste tous les tests à exécuter
- Génère un rapport HTML

### 3. CI/CD

Intégrer dans GitHub Actions :
- Validation des dépendances à chaque PR
- Génération automatique des diagrammes
- Mise à jour automatique de la documentation

---

## 📚 Références

### Documentation créée :

1. **DEPENDENCIES_MAP.md**
   - Cartographie textuelle
   - 11 sections principales
   - Matrice de dépendances
   - Règles de maintenance

2. **docs/DEPENDENCY_GRAPH.md**
   - 7 diagrammes Mermaid
   - Légende complète
   - Instructions d'utilisation

3. **scripts/SCRIPTS_REFERENCE.py**
   - Champ "called_by" ajouté
   - Affichage amélioré

---

## 🎉 Conclusion

Le système centralisé est maintenant **complet** avec :

✅ Catalogue des scripts et tests  
✅ **Cartographie des dépendances**  
✅ **Diagrammes visuels**  
✅ Documentation exhaustive  
✅ Venv garanti pour les tests  
✅ Fichiers .bat pour exécution simple  

**Plus aucune question du type "qui appelle quoi ?" ne restera sans réponse !**

---

**Date de création** : 2025-11-10  
**Auteur** : Système centralisé v2.0  
**Version** : 2.0 (ajout cartographie)
