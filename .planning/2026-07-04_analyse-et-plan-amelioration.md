# 📋 Planification : Analyse complète du programme & Plan d'amélioration

**Date de création** : 2026-07-04
**Statut** : 🟡 En cours (plan soumis pour validation — aucun code modifié)
**Priorité** : Haute

---

## 🎯 Vue d'ensemble

### Description de la demande
> « Respire un grand coup et analyse l'entièreté du programme étape par étape. Pour améliorer, si tu as des idées n'hésite pas. Je désire un plan md avant. »

### Objectif
Cartographier l'ensemble du pipeline (GUI → génération → entraînement → détection), identifier les bugs, les incohérences, le code mort et la dette technique, puis proposer un plan d'amélioration par phases, validé **avant** toute modification de code.

### Impact attendu
- **Utilisateur** : application plus fiable (moins de crashs silencieux), démarrage plus clair, documentation à jour
- **Technique** : suppression des doublons, source unique de vérité pour le mapping de classes, tests automatisés
- **Documentation** : README corrigé (liens cassés), consolidation docs/ vs docs/new vs docs/archive

---

## 🔍 PARTIE 1 — Analyse étape par étape du programme

### 1.1 Architecture globale

```
START.bat / INSTALL.bat          → lanceurs Windows (.venv)
GUI_v3.1_modern.py  (8 926 lignes)  → interface Tkinter monolithique (2 classes : SettingsDialog, ModernPokemonGUI)
core/               (~6 850 lignes) → 17 modules métier
scripts/            (21 scripts)    → maintenance, migration, merge_dataset
tests/              (24 fichiers)   → scripts de test ad hoc (non pytest)
tools/              (~15 outils)    → création exe, banner, téléchargement
config/             → paths.json, gui_config.json, ui_messages*.json, requirements*.txt
models/             → cards_database.yaml (source de vérité cartes + prix)
obsolete/           → anciens fichiers conservés dans le repo
```

### 1.2 Flux du pipeline (workflow_manager.py)

1. **Téléchargement** (`image_downloader.py` + `tcgdex_api.py`) : récupère les cartes d'un set via l'API TCGdex → `images/`
2. **Augmentation** (`augmentation_albumentations.py`) : ~25 transformations Albumentations → `output/augmented/` (lancé en **subprocess**)
3. **Holographique** (`holographic_augmenter_optimized.py`) : effets rainbow/metallic/glare (vectorisé, GPU optionnel)
4. **Mosaïques** (`mosaic_optimized.py`) : compositions multi-cartes annotées YOLO → `output/mosaics/` (subprocess)
5. **Merge** (`scripts/merge_dataset.py`) : fusion augmented + mosaics → `output/dataset/` + `data.yaml` (import Python direct)
6. **Validation** (`dataset_validator.py`) : rapport HTML (optionnel, non bloquant)
7. **Balancing** (`auto_balancer_optimized.py`) : équilibrage des classes (optionnel)
8. **Entraînement** (`training_manager.py`) : YOLOv8/v11 via ultralytics
9. **Détection** (`detection_manager.py`) : webcam/vidéo/image + prix Cardmarket/TCGPlayer

### 1.3 Points forts constatés ✅

- Séparation GUI / core plutôt propre (managers avec callbacks de log et progression)
- Migration imgaug → Albumentations faite (NumPy 2.x OK, commit v3.4.0)
- Chemins centralisés dans `config/paths.json`, messages UI centralisés (fr/en)
- Dataclasses de config avec validation `__post_init__`
- Versions « optimized » réellement vectorisées (multiprocessing + GPU optionnel)
- Système de planification `.planning/` déjà en place

---

## 🐛 PARTIE 2 — Problèmes identifiés

### 2.1 Bugs probables (priorité haute)

| # | Fichier | Problème | Effet |
|---|---------|----------|-------|
| B1 | `core/workflow_manager.py:351` | `import merge_dataset` : le fichier est dans `scripts/`, qui n'est **pas** dans `sys.path` en exécution standalone (le GUI l'ajoute seulement à la ligne 7167) | Étape merge crash en CLI (`python core/workflow_manager.py`) |
| B2 | `core/utils.py:480-490` | `load_prices(yaml_path=None)` appelle `os.path.exists(None)` | `TypeError` si appelé sans argument |
| B3 | `core/utils.py:227` vs `core/augmentation_albumentations.py:514` | **Mapping de classes incohérent** : `utils.load_card_data` démarre `class_id = 1`, la copie locale d'`augmentation_albumentations` démarre à 0 (« YOLO utilise 0-indexed ») | Décalage potentiel des labels selon le chemin de code (les scripts `fix_class_mapping*.py` témoignent d'incidents passés) |
| B4 | `core/augmentation_albumentations.py:482` | Fallback `class_id = hash(filename) % 1000` si carte inconnue | Labels aléatoires silencieux → dataset corrompu sans erreur |
| B5 | `core/workflow_manager.py:370` | L'étape merge est enregistrée comme `WorkflowStep.MOSAIC` (« pas de MERGE défini ») | Résumé faux + `is_success()` ambigu |
| B6 | `scripts/merge_dataset.py:14` | `load_paths()` lit `config/paths.json` en chemin **relatif au CWD** (utils.py utilise `__file__`, lui) | Crash si lancé depuis un autre répertoire |

### 2.2 Duplication de code (priorité haute)

- `load_card_data` existe en **3 exemplaires** : `core/utils.py`, `core/augmentation_albumentations.py:503`, `core/mosaic_optimized.py:83` — avec des comportements différents (cf. B3)
- `extract_card_number` dupliqué : `core/utils.py:254` et `core/augmentation_albumentations.py:546`, `core/mosaic_optimized.py:101`
- `detection_with_prices.py` (308 l.) ≈ sous-ensemble de `detection_manager.py` (619 l.)
- `augmentation_optimized.py` (imgaug, remplacé en v3.4.0) coexiste avec `augmentation_albumentations.py`

### 2.3 Code mort / héritage (priorité moyenne)

- `obsolete/` versionné dans le repo (12+ fichiers), `README_old.md` à la racine
- `core/augmentation_optimized.py` : dépend d'imgaug qui n'est **plus dans requirements.txt** → import cassé
- Docs en triple : `docs/`, `docs/new/`, `docs/archive/v3.3.1/` + `docs/migration/`
- ~23 `except:` nus dans core + GUI (erreurs avalées silencieusement)

### 2.4 README & documentation (priorité moyenne)

- **Liens cassés dans README.md** : `docs/README_COMPLET.md`, `docs/GUI_V3_GUIDE.md`, `docs/MAINTENANCE_SCRIPTS_REFERENCE.md` n'existent plus (déplacés vers `docs/archive/v3.3.1/`)
- README annonce « v3.2 » et « imgaug » alors que le code est en v3.4 / Albumentations
- `docs/new/` semble être la doc réorganisée v4.0 mais n'est référencée nulle part depuis le README racine

### 2.5 Robustesse & architecture (priorité moyenne/basse)

- `GUI_v3.1_modern.py` : **8 926 lignes, 169 méthodes dans 2 classes** — difficile à maintenir ; ~22 `threading.Thread` créés à la main sans pool ni gestion d'annulation uniforme
- Communication GUI↔core par **subprocess + parsing stdout** pour augmentation/mosaïques alors que les modules sont importables (perte des exceptions, encodage Windows fragile)
- `print()` partout au lieu de `logging` (le logger existe dans workflow_manager mais n'est configuré nulle part)
- Portage : lanceurs `.bat` uniquement → projet inutilisable tel quel sous Linux/macOS (même si Tkinter/YOLO le permettraient)
- Tests : 24 fichiers ad hoc à lancer à la main, **aucun CI** (pas de workflow GitHub Actions), pas de pytest
- Pas de `pyproject.toml` : installation par requirements éclatés en 3 fichiers dans `config/`

---

## 📝 PARTIE 3 — Plan d'amélioration par étapes

### Phase 1 : Corrections de bugs (sans changement d'architecture)
**Statut** : ⏳ À faire — **Effort : ~½ journée**

**Actions** :
- [ ] B1 : ajouter `scripts/` au `sys.path` dans `workflow_manager._run_merge` (ou déplacer `merge_dataset.py` vers `core/`)
- [ ] B2 : corriger `load_prices` (défaut depuis `PATHS` avant le `os.path.exists`)
- [ ] B3 : **unifier le mapping de classes** — une seule fonction dans `core/utils.py`, indexation 0 (standard YOLO), supprimer les copies locales
- [ ] B4 : remplacer le fallback `hash()` par un warning explicite + skip de l'image
- [ ] B5 : ajouter `WorkflowStep.MERGE` à l'enum
- [ ] B6 : résoudre `paths.json` via `Path(__file__)` dans `merge_dataset.py`

**Fichiers concernés** : `core/workflow_manager.py`, `core/utils.py`, `core/augmentation_albumentations.py`, `core/mosaic_optimized.py`, `scripts/merge_dataset.py`

**Validation** :
- [ ] `python core/workflow_manager.py` fonctionne en standalone
- [ ] Un dataset généré avant/après a des class_id identiques et 0-indexés
- [ ] Tests de non-régression sur `extract_card_number` et `load_card_data`

---

### Phase 2 : Nettoyage (code mort + doc)
**Statut** : ⏳ À faire — **Effort : ~½ journée**

**Actions** :
- [ ] Supprimer `obsolete/`, `README_old.md`, `core/augmentation_optimized.py` (imgaug), `core/detection_with_prices.py` (après vérif qu'aucun script ne l'importe)
- [ ] Consolider la doc : `docs/new/` devient la doc officielle, `docs/archive/` conservé, supprimer les doublons
- [ ] Corriger les liens cassés du README + mettre à jour version (v3.4) et mention Albumentations
- [ ] Remplacer les `except:` nus par des exceptions ciblées + log

**Validation** :
- [ ] `grep -rn "detection_with_prices\|augmentation_optimized"` → 0 référence active
- [ ] Tous les liens du README résolvent

---

### Phase 3 : Tests & CI
**Statut** : ⏳ À faire — **Effort : ~1 journée**

**Actions** :
- [ ] Convertir les tests critiques en pytest : `extract_card_number`, `load_card_data`, génération labels YOLO, merge/split
- [ ] Ajouter `tests/conftest.py` + fixtures (mini-dataset de 3 cartes)
- [ ] GitHub Actions : lint (ruff) + pytest sur push/PR (Ubuntu + Windows)
- [ ] Créer `pyproject.toml` (dépendances regroupées, extras `[training]`, `[dev]`)

**Validation** :
- [ ] `pytest` vert en local et en CI

---

### Phase 4 : Refactorisation GUI (optionnelle, plus ambitieuse)
**Statut** : ⏳ À faire — **Effort : 2-3 journées** — ⚠️ à valider séparément

**Actions** :
- [ ] Découper `GUI_v3.1_modern.py` en package `gui/` (dashboard, onglets, settings, thème, widgets)
- [ ] Remplacer subprocess+parsing par appels directs aux managers dans des threads, avec une file de messages unique vers le GUI
- [ ] Centraliser le threading (un seul « TaskRunner » avec annulation)
- [ ] `logging` configuré globalement (fichier + panneau de log GUI)
- [ ] Lanceurs cross-platform (`start.sh` / entry point `pokemon-dataset-gen` via pyproject)

**Validation** :
- [ ] Checklist `docs/migration/CHECKLIST_TEST_GUI.md` repassée entièrement

---

## 🔧 PARTIE 4 — Cibles de refactorisation supplémentaires (ajout 2026-07-04)

Analyse approfondie suite à la question « que pourrait-on refactoriser encore ? ». Classées par gain/risque.

### R1. Thread-safety du GUI ⚠️ (gain élevé — c'est aussi un bug latent)
`log()` (`GUI_v3.1_modern.py:5910`) manipule directement les widgets Tkinter et est appelé depuis les threads workers ; ~140 appels `messagebox.*` dont beaucoup depuis des threads ; seulement 4 usages de `.after()`. **Tkinter n'est pas thread-safe** → freezes/crashs aléatoires possibles.
**Refactor** : une `queue.Queue` de messages + un poller `root.after(100, ...)` unique qui fait les `insert` et affiche les messageboxes dans le thread principal.

### R2. Bloc subprocess copié-collé ~12× dans le GUI (gain élevé, risque faible)
Le pattern « `Popen` → `iter(stdout.readline)` → `self.log` → `wait()` → messagebox succès/échec → `end_operation` » est dupliqué dans `start_augmentation`, `start_mosaic`, `start_merge_dataset`, `start_validation`, `start_export`, `start_balancing`, `start_holographic`, `start_fake_generator`, etc. (~40-70 lignes chacun).
**Refactor** : une méthode générique `run_task(name, cmd_ou_callable, on_success)` — les 12 méthodes `start_*` tombent à ~10 lignes chacune (≈ -700 lignes).

### R3. Mixin/base commune pour les managers core (gain moyen)
`workflow_manager`, `training_manager`, `detection_manager` (+ `image_downloader` en variante) réimplémentent chacun `set_log_callback` / `_log` / `_progress_callback`. Les 6 méthodes `_run_*` de `workflow_manager` répètent le même squelette de 45 lignes (chrono + try/except + StepResult).
**Refactor** : classe `BaseManager` (log/progress) + helper `_execute_step(step, fn)` qui factorise chrono/statut/erreurs.

### R4. Unifier resize/chargement d'images (gain moyen)
`resize_cards` existe dans `utils.py:301`, `augmentation_albumentations.resize_cards_batch:359`, `mosaic_optimized.resize_cards_parallel:168` — trois implémentations du même besoin (chargement + RGBA→RGB + resize), en plus des doublons `load_card_data`/`extract_card_number` déjà notés en 2.2.
**Refactor** : un seul module `core/image_io.py` avec version séquentielle et parallèle.

### R5. Externaliser la config GUI et le thème (gain moyen)
- Lecture/écriture de `gui_config.json` dupliquée entre `SettingsDialog.load_settings` et le GUI principal (6 accès directs, 7 `json.load/dump`) → une classe `GuiConfig` unique (load/save/défauts).
- ~42 couleurs hex codées en dur hors du dict `self.colors` → tout passer par la palette, prérequis pour un vrai thème clair/sombre.
- `SettingsDialog` (1 650 lignes) à extraire en module dès la Phase 4.

### R6. i18n incomplète (gain faible/moyen)
Le système `ui_messages.json`/`get_message()` existe, mais ~160 chaînes « Succès/Erreur/Error/Success » sont codées en dur dans le GUI, en mélange français/anglais.
**Refactor** : basculer les messageboxes et logs GUI sur `get_message()` (mécanique, peut se faire progressivement).

### R7. Consolider les scripts quasi-doublons (gain faible, rapide)
- `init_prices.py` / `init_prices_simple.py` / `init_prices_real.py` → un seul `init_prices.py --mode {full,simple,manifest}`
- `update_prices_yaml.py` / `update_prices_yaml_fast.py` → un seul avec `--fast`
- `fix_class_mapping.py` / `fix_class_mapping_correct.py` et `create_card_mapping.py` / `create_real_mapping.py` → garder la bonne version, archiver l'autre
- `tests/` : séparer les vrais tests des utilitaires `debug_*` / `verify_*` / `visualize_*` (à déplacer vers `tools/diagnostics/`)

### R8. Remplacer subprocess par des imports directs (gain élevé, risque moyen)
Le GUI **et** `workflow_manager` lancent `augmentation_albumentations.py`, `mosaic_optimized.py`, `dataset_validator.py`, `auto_balancer_optimized.py` en sous-processus avec parsing de stdout, alors que ce sont des classes importables du même package. Conséquences actuelles : exceptions perdues, encodage Windows fragile, pas de progression structurée.
**Refactor** : appeler les classes directement (les callbacks log/progress existent déjà) ; garder le subprocess uniquement pour l'entraînement YOLO (isolation mémoire GPU justifiée). C'est le cœur de la Phase 4.

### Intégration au plan de phases
- **Phase 1** (bugs) : + R1 (thread-safety = correctif de fiabilité)
- **Phase 2** (nettoyage) : + R7 (scripts doublons)
- **Phase 3** (tests/CI) : inchangée — les tests protègent les refactors suivants
- **Phase 4** (GUI) : R2, R3, R5, R8 en font partie ; R4 et R6 en continu

---

### 💡 Idées bonus (backlog, non planifiées)
- Cache HTTP TCGdex sur disque + reprise de téléchargement
- Export du modèle en ONNX/TensorRT exposé dans le GUI (le code existe déjà côté training_manager)
- Aperçu temps réel des augmentations dans le GUI avant génération
- Migration éventuelle du GUI vers PySide6 ou NiceGUI (si Tkinter devient limitant)
- Publication PyPI ou exe auto-build via CI

---

## 📊 Suivi des progrès

### Timeline
```
[Plan] ──[Phase 1: Bugs]──[Phase 2: Nettoyage]──[Phase 3: Tests/CI]──[Phase 4: GUI]──> [Fin]
  ✅          ⏳                 ⏳                    ⏳                  ⏳
```

### Progression globale
- **Avancement** : 0 / 4 phases (plan livré, en attente de validation)
- **Blocages actuels** : validation utilisateur du périmètre (surtout Phase 4)

---

## ❓ Questions de clarification

1. **Périmètre de la Phase 4 (refonte GUI)** — gros chantier : la faire maintenant, plus tard, ou jamais ?
   - Recommandation : Phases 1-3 d'abord ; Phase 4 seulement si le GUI doit encore évoluer.
2. **Suppression de `obsolete/`** — OK pour suppression définitive (l'historique git conserve tout) ?
3. **Support Linux/macOS** — souhaité, ou Windows-only assumé ?

---

## ✅ Checklist finale (par phase)

- [ ] Étapes complétées et validées
- [ ] Tests passent (pytest à partir de la Phase 3)
- [ ] README + docs/CHANGELOG.md mis à jour (règle absolue #1 du projet)
- [ ] Pas de régression sur le pipeline Generate → Train → Detect
- [ ] Commit par phase, messages descriptifs
