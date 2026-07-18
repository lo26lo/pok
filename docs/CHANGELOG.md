# 📜 Changelog

All notable changes to the Pokémon Dataset Generator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### 🔧 Correctifs de l'audit de juillet 2026 (20 bugs corrigés)

Corrections des findings du rapport `docs/BUG_RESEARCH_2026-07.md`
(7 critiques, 5 élevés, 8 moyens — statut ✅/📝 détaillé dans le rapport) :

- **fix(core)** : `generate_yaml_from_manifest` FUSIONNE désormais avec la
  base existante au lieu de l'écraser — cartes des autres sets, prix et
  class_id YOLO préservés (C1)
- **fix(core)** : workflow automatique — l'étape mosaïques utilise
  `--max-groups` (quick=25, standard=62, custom=N, complete=∞) au lieu du
  mode `all` non implémenté qui réussissait sans rien produire (C2, C3)
- **fix(core)** : auto-balancer — les bboxes des images `_balN` sont
  corrigées pour le flip ET le scale (mesure de la transformation réelle via
  3 keypoints), comptage par image et non par occurrence, images préchargées
  réellement utilisées (C4, E2, M9)
- **fix(core)** : auto-balancer — `train.txt`/`val.txt` sont mis à jour après
  balancing (nouvelles images ajoutées au train, fichiers supprimés retirés,
  split val préservé) (C5)
- **fix(core)** : tcgdex_api — codes de sets corrigés et alignés sur
  `POPULAR_SETS` (Obsidian Flames=sv03, Paradox Rift=sv04, 151=sv03.5…),
  prix à 0.0 acceptés, padding du localId testé dans les deux variantes
  (C6, M5)
- **fix(core)** : workflow — stratégies `undersample`/`remove` traduites en
  `reduce` pour le balancer ; sous-processus lus en UTF-8 tolérant (C7, M6)
- **fix(core)** : mosaïques — bboxes clippées au canvas dans les layouts 1-3
  (parité avec le layout 4) ; dossiers `corrupted/` et fonds web ancrés dans
  `output/` au lieu du CWD (E3, M8)
- **fix(core)** : detection/training — device auto-détecté (`0` si CUDA
  disponible, sinon `cpu`) ; annotation depuis `orig_img` Ultralytics au lieu
  d'une relecture disque (E4)
- **fix(core)** : fallback de `load_paths()` complété avec toutes les clés
  requises par les modules (E5) ; effet holographique — gradient normalisé
  min-max (angles > 90°) et palette convertie en BGR (M3) ; export Roboflow —
  `names` indexé par class_id (M7) ; scanner de collection — expiration des
  tracks non confirmés après 10 s (M10)
- **fix(scripts)** : workflow_optimized appelle `scripts/merge_dataset.py`
  (chemin corrigé) (E1) ; merge_dataset — garde contre les sources vides,
  paires image+label complètes uniquement, fallback des noms de classes si
  `data.yaml` est présent mais sans `names` (M1)
- Suite de tests : 281 passés, 0 échec (7 skips liés aux dépendances)

### 🐛 Audit : recherche approfondie de bugs (juillet 2026)

- Nouveau rapport `docs/BUG_RESEARCH_2026-07.md` : audit ligne à ligne des
  25 modules du core + orchestration (workflow, merge, GUIs)
- 7 bugs critiques identifiés (écrasement de `cards_database.yaml` à chaque
  téléchargement de set, étape mosaïques du workflow en no-op silencieux,
  bboxes faussées par le scale de l'auto-balancer, mapping TCGdex des sets
  décalé, balancing invisible pour train.txt…), 5 élevés, 11 moyens,
  9 mineurs — aucun correctif appliqué dans ce commit (recherche seule)

### 🖥️ GUI Qt : parité fonctionnelle avec les vagues 3 & 4

- Rebase de l'interface PySide6 sur `main` (10 features F01–F10 intégrées) —
  le GUI Qt était en retard sur les fonctionnalités récentes, désormais
  à parité :
  - **Vue Détection** : cases « 🎴 Identifier les cartes » (F01) et
    « 🔍 Estimer l'état » (F02), bouton « 🧺 Scan de collection » + récap
    et « 📂 Dossier des scans » (F03), carte « 💾 Prix hors-ligne » avec
    indicateur de snapshot + « ⬇ Précharger les prix » (F10)
  - **Fenêtre « 💹 Price History »** (`gui_qt/price_history_dialog.py`) :
    sparkline dessinée au QPainter, synthèse actuel/min/max/tendance,
    gestion des alertes de seuil (F09)
  - **Vue Augmentation** : intensité globale, nombre de transformations et
    catégories passés à la génération via les drapeaux CLI (F06)
- 8 nouveaux tests (`tests/test_gui_qt.py`) — suite : 334 passés, 0 échec

### ✨ Backlog F05 : mains plus réalistes dans les mosaïques

- Doigts procéduraux avec **ongles** (ellipse claire + lunule, visible
  paume vers soi ~50 % des cas) et **pouce** au premier plan (plus large,
  incliné, ongle toujours visible) dans ~70 % des mains
- **Éventails tenus depuis le bord bas** du canvas (~35 % des éventails,
  layout 4) : main de joueur au premier plan, bas des cartes coupé par le
  cadre — bboxes clippées et filtre de visibilité < 25 % déjà en place ;
  doigts systématiques sur ces éventails
- GUI : bouton « 📂 Open Scans Folder » dans la vue Detection (backlog F03)
- 5 nouveaux tests — suite : 319 passés, 0 échec

### ✨ Backlog F06 : les paramètres calibrés pilotent la génération

- La génération d'augmentations accepte enfin `intensity`,
  `n_transforms` et `categories` (CLI : `--intensity/--transforms/
  --categories`) — jusqu'ici la Live Preview permettait de calibrer des
  paramètres que la génération ignorait (toujours intensity=1.0)
- Nouveau bouton « 💾 Use for generation » dans la Live Preview :
  sauvegarde la calibration dans `config/augmentation_params.json`,
  lue par défaut par la génération (GUI, workflow ET CLI) ; les drapeaux
  CLI explicites restent prioritaires ; sans fichier, comportement de
  production historique inchangé (intensity=1.0, 3-6 transfos, toutes
  catégories)
- 🐛 **Fix** : le CLI d'augmentation rejetait les arguments envoyés par
  la GUI et le workflow (`--num_aug/--source/--target` vs
  `--count/--input/--output`) — l'étape d'augmentation plantait en
  argparse error ; les deux jeux d'arguments sont désormais acceptés
  (`--target X` → `output/X`)

### ✨ Backlog F03+F02 : valeur d'inventaire pondérée par l'état

- Le scan de collection agrège le grading F02 quand il est actif :
  chaque carte de l'inventaire retient le **meilleur état observé**
  (les frames floues/en biais sous-estiment l'état) et sa valeur est
  pondérée par le facteur de condition (NM 1.0 → PL 0.5)
- Colonne `condition` dans les exports CSV/Excel ; totaux pondérés
- 15 nouveaux tests (`tests/test_generation_params.py`) —
  suite : 314 passés, 0 échec

### ✨ F02 : Estimation de l'état de la carte (grading)

- `core/card_grader.py` : estimation best effort de l'état depuis le crop
  webcam — **centrage** mesuré par profils de gradients (premier edge
  significatif depuis l'extérieur = transition bordure→cadre), précision
  ±3 % mesurée (critère : ±5 %) ; **coins abîmés** détectés par
  blanchiment (pixels clairs ET désaturés, toutes couleurs de bordure),
  arrondi de la carte masqué, neutre sur bordure blanche ; **rayures hors
  périmètre v1** (résolution webcam insuffisante — décision de design)
- Barème NM/EX/GD/PL, facteur de prix 1.0/0.85/0.70/0.50, ~3 ms par carte
- Overlay : badge d'état (« Skiploom [swsh7 003] [NM] ») et **prix
  pondéré par l'état** ; jamais bloquant (la détection continue sans
  grading si le crop est inexploitable)
- Activation : case « 🔍 Grade Cards » (vue Detection) ou CLI `--grade` ;
  champs condition/condition_score/price_factor sur `Detection`
- 22 nouveaux tests (`tests/test_card_grader.py`) —
  suite : 299 passés, 0 échec

### ✨ F09 : Historique et alertes de prix

- L'historique s'appuie sur la table append-only de F10 (chaque relevé de
  préchargement est conservé, persistant entre sessions) — pas de couche
  de persistance supplémentaire
- Alertes de seuil persistantes (`price_alerts` en SQLite) : notifier
  quand une carte **dépasse** (`above`) ou **passe sous** (`below`) un
  prix ; cycle fiable sans spam — l'alerte se désarme au déclenchement et
  se réarme quand la condition redevient fausse
- Alertes évaluées à chaque relevé (fin de préchargement CLI et GUI) :
  log « 🔔 ALERTE PRIX » + notification GUI
- `gui/price_history_view.py` : fenêtre « 💹 Price History » — sparkline
  de l'évolution (canvas Tk pur, zéro dépendance graphique), synthèse
  (actuel/min/max/tendance), création/suppression d'alertes, bouton
  « Check alerts »
- 23 nouveaux tests (`tests/test_price_alerts.py`) —
  suite : 277 passés, 0 échec

### ✨ F10 : Cache API hors-ligne (snapshot des prix)

- `core/price_cache.py` : snapshots de prix **append-only** en SQLite
  (`models/price_cache.db`) — chaque relevé est horodaté, la table sert
  aussi d'historique (socle de F09) ; TTL de fraîcheur 24 h (pilote le
  rafraîchissement : hors-ligne, une entrée périmée est toujours servie
  avec sa date) ; purge pour borner l'historique par carte
- `TCGdexAPI(cache=...)` + `get_card_prices()` : couche transparente —
  cache frais → API (enregistrée au passage) → cache périmé en mode avion
  (« 📴 prix du JJ/MM ») ; variantes de padding du localId gérées
  (sv08-019 vs swsh7-3)
- `load_prices_with_cache()` : base YAML recouverte par les snapshots —
  **détection et scan de collection 100 % fonctionnels sans réseau**
  après préchargement
- `tools/preload_prices.py` : préchargement d'un set (`--set sv08`),
  de la base (`--database`) ou d'un inventaire de scan F03
  (`--inventory scan.csv`) ; `--check` et `--purge N`
- GUI : indicateur « 💾 N prix, snapshot du JJ/MM » + bouton
  « ⬇ Preload Prices » dans la vue Detection
- 27 nouveaux tests (`tests/test_price_cache.py`) —
  suite : 254 passés, 0 échec

### ✨ F03 : Mode « scan de collection »

- `core/collection_scanner.py` : session de détection continue qui
  **déduplique** les cartes vues et construit un inventaire — une carte
  est confirmée après 3 frames d'identification (une même carte présentée
  10 s n'apparaît qu'une fois), deux exemplaires côte à côte comptent
  pour une quantité de 2 (max de détections simultanées)
- Prix par card_id depuis la base locale (models/cards_database.yaml,
  intégration Cardmarket/TCGPlayer existante) — agrégats : cartes uniques,
  exemplaires, valeur totale min-max, durée de session
- Export **CSV + Excel** (openpyxl optionnel) dans
  `output/collection_scans/`, avec ligne de totaux
- Webcam : compteur live sur l'overlay (« Scan: 3 cartes (4 ex.) |
  12.50 EUR »), confirmations loggées en direct ;
  CLI `python core/detection_manager.py <model> --webcam --scan`
- GUI : bouton « 🧺 START COLLECTION SCAN » (vue Detection) avec récap de
  fin de session ; **mode dégradé** par classe YOLO si l'index F01 manque
- 22 nouveaux tests (`tests/test_collection_scanner.py`) —
  suite : 227 passés, 0 échec

### ✨ F01 : Identification fine de la carte (embeddings + index)

- `core/card_identifier.py` : 2ᵉ étage de pipeline — après la localisation
  YOLO, le crop de chaque bbox est identifié (set + numéro) par recherche
  du plus proche voisin cosinus dans un index d'embeddings construit sur
  les images TCGdex téléchargées ; **fonctionne sur des sets jamais vus
  par YOLO**, sans réentraînement
- Embedder par défaut : features MobileNetV2 1280-d via cv2.dnn
  (`models/mobilenetv2_embeddings.onnx`, 9 Mo, tronqué à la couche
  global-pool — aucune dépendance Python ajoutée) ; fallback « classic »
  (grille Lab + gradients, pur OpenCV) si l'ONNX est absent
- Recherche : FAISS (`faiss-cpu`, optionnel) avec fallback numpy
  automatique ; références indexées en moyenne de 3 vues (native, 300 px,
  300 px floutée) pour rapprocher l'index du domaine webcam
- **Benchmark sur 245 cartes réelles** (requêtes dégradées type webcam :
  perspective, éclairage, flou, bruit, JPEG, basse résolution) :
  98,4 % top-1, 100 % top-5, ~7 ms par carte sur CPU
  (`tools/benchmark_card_embeddings.py`) — critères F01 (≥ 90 %, < 50 ms)
  dépassés
- `tools/build_card_index.py` : construction de l'index depuis `images/`
  (`--check` pour l'état, `--download-model` pour récupérer l'ONNX)
- Détection : option `identify_cards` (GUI : case « 🎴 Identify Cards »,
  CLI : `--identify`) — l'overlay affiche le nom exact + set + numéro
  (« Skiploom [swsh7 003] ») et le prix est cherché directement par
  card_id ; jamais bloquant si l'index manque
- 33 nouveaux tests (`tests/test_card_identifier.py`) —
  suite : 205 passés, 0 échec

### ✨ F07 : Onglet « 📊 Evaluation » dans la GUI

- `core/run_analyzer.py` : parsing des artefacts Ultralytics
  (results.csv, args.yaml, courbes PNG), résumé du run au meilleur epoch,
  comparaison A/B (deltas), historique real_mAP (F08) rattaché au run ;
  score d'erreur par image (IoU + appariement glouton : manqués, faux
  positifs, mauvaise classe) et planche contact annotée des pires
  prédictions (GT en vert, prédictions en rouge)
- `gui/evaluation_view.py` : nouvelle vue sidebar « 📊 Evaluation » —
  sélecteur de run, métriques + hyperparamètres, boutons d'artefacts
  (courbes, confusion, PR/F1, aperçus val), comparaison entre deux runs,
  bouton « Pires prédictions » (rejoue le best.pt du run sur le set réel
  F08 ou la val synthétique, en thread + file pollée)
- Aucun recalcul : les PNG d'Ultralytics sont réutilisés tels quels
- 19 nouveaux tests (`tests/test_run_analyzer.py`) + smoke test xvfb —
  suite : 172 passés, 0 échec

### ✨ F08 : Set de validation réel (métrique real_mAP)

- `datasets/real_val/` : structure images/ + labels/ (format YOLO) avec
  **protocole de capture reproductible** documenté (README du dossier) —
  photos de vraies cartes, jamais utilisées à l'entraînement
- `core/real_validation.py` : état du set (`--check`), validation des
  labels YOLO (format, bornes, classes), **garde anti-fuite par hash MD5**
  (l'évaluation est refusée si une image du set réel est retrouvée dans
  les dossiers d'entraînement), évaluation `real_mAP` via Ultralytics,
  rapport JSON avec historique (`output/real_val_report.json`) pour
  comparer les runs avant/après F04/F05
- `core/training_manager.py` : évaluation real_mAP automatique en fin
  d'entraînement si le set est prêt (jamais bloquante)
- `tools/preannotate_real_val.py` : pré-annotation assistée des photos
  par le modèle courant (brouillon à corriger à la main)
- 20 nouveaux tests (`tests/test_real_validation.py`) —
  suite : 153 passés, 0 échec

### ✨ F06 : Prévisualisation live des augmentations (GUI)

- `core/augmentation_albumentations.py` : le pool de 25 transformations est
  désormais construit par `build_transform_pool(intensity, categories)` —
  intensité globale réglable (0.1×–2×) et filtrage par catégorie ;
  **intensity=1.0 reproduit exactement le pipeline de production**
  (aucune régression, vérifié par test dédié)
- `preview_augmentations()` : variantes générées EN DIRECT (aucun
  sous-processus, aucune écriture disque), reproductibles via seed
  (compatible albumentations 1.x et 2.x)
- `gui/augmentation_preview.py` : fenêtre « 👁 Live Preview » — sliders
  intensité / nb de transformations, 6 cases catégories, grille
  original + 6 variantes, debounce 350 ms, rendu en thread avec file de
  résultats pollée par le thread principal (règle v3.6 : aucun appel Tk
  depuis un worker) ; aperçus via PhotoImage base64 (pas de dépendance
  Pillow) ; bouton ajouté dans la vue Augmentation
- 17 nouveaux tests (`tests/test_augmentation_preview.py`) + smoke test
  xvfb complet — suite : 133 passés, 0 échec

### ✨ F05 : Occlusions réalistes (éventails, sleeves, doigts)

- `core/occlusion_effects.py` : effets d'occlusion procéduraux —
  `apply_sleeve` (voile plastique + reflet spéculaire, dimensions
  inchangées), `fan_layout` (éventail sur arc de cercle autour d'un
  pivot « poignet »), `add_fingers` (doigts procéduraux, teintes de peau
  variées), `compute_visible_fractions` (fraction visible par carte
  après empilement, buffer d'étiquettes sous-échantillonné)
- `core/mosaic_optimized.py` : nouveau **layout_mode 4** (éventail/main)
  — cartes qui se chevauchent avec ombres inter-cartes, sleeve aléatoire
  (50 %), doigts sur certains éventails ; les cartes visibles à moins de
  25 % ne sont **jamais** annotées ; bboxes clippées au canvas
- GUI : option « 4 - Fan / Hand (Occlusions) » dans Settings → Mosaic
- 15 nouveaux tests (`tests/test_occlusion_effects.py`) —
  suite complète : 111 passés, 0 échec

### ✨ F04 : Fonds réalistes procéduraux pour les mosaïques

- `core/background_generator.py` : générateur procédural de fonds
  (5 catégories : table en bois, tapis de jeu, page de classeur, tissu,
  bureau) — 100 % NumPy/OpenCV, hors-ligne, sans problème de licence,
  reproductible via seed
- Ombres portées douces sous les cartes (`add_drop_shadow`, masque alpha
  flouté + décalage aléatoire) et effets caméra photométriques
  (`apply_camera_effects` : température de couleur, exposition, éclairage
  directionnel, vignettage) — les annotations restent valides
- `core/mosaic_optimized.py` : nouveau **background_mode 3** (fond réaliste
  généré à la volée, ombres + effets caméra automatiques)
- GUI : option « 3 - Realistic (Procedural) » dans Settings → Mosaic
- `tools/generate_realistic_backgrounds.py` : pré-génération sur disque et
  galerie de contrôle visuel (`--gallery`)
- 17 nouveaux tests (`tests/test_background_generator.py`) —
  suite complète : 96 passés, 0 échec
- Suivi : `docs/JOURNAL_FEATURES.md` (journal des features F01–F10)

## [3.7.0] - 2026-07-04

### 🖥️ Nouvelle interface Qt (PySide6) — thème clair/sombre

#### Package `gui_qt/` (~2 300 lignes, remplace les ~7 100 lignes Tkinter)
- `app.py` : fenêtre principale — sidebar de navigation (11 vues),
  vues empilées, dock de logs, barre de statut avec progression + Stop
- `theme.py` : **thème sombre (Catppuccin Mocha, identique à l'historique)
  ET thème clair (Catppuccin Latte)**, commutables à chaud, persistés
- `bridge.py` : QtTaskBridge — le TaskRunner (Phase 4) branché sur des
  signaux Qt, thread-safe nativement (plus de file manuelle)
- `views/` : un module par écran — home (stats + workflow auto), download
  (TCGdex + régénération auto de la base), augmentation (+ pipeline holo),
  mosaïques, validation & merge, export, training (presets Jetson inclus,
  export ONNX/TensorRT), détection (webcam/image/dossier + prix), fake
  images, tools, settings (7 onglets déclaratifs sur GuiConfig)
- `GUI_qt.py` : point d'entrée

#### Partage de code
- `core/manifest_tools.py` : génération de cards_database.yaml depuis le
  manifest extraite du GUI Tkinter — partagée par les deux interfaces
- Le fichier `gui_config.json` est commun aux deux GUIs (mêmes clés)

#### Lanceurs
- `START.bat` et `start.sh` lancent l'interface Qt
- Interface Tkinter conservée en secours : `START_LEGACY.bat` /
  `start.sh --legacy` (suppression prévue après validation sur poste réel)

#### Tests & CI
- 7 tests pytest-qt exécutés **offscreen y compris en CI**
  (navigation, thèmes, bridge succès/échec/état busy, settings roundtrip)
- CI : PySide6 + pytest-qt installés, `QT_QPA_PLATFORM=offscreen`,
  bibliothèques Qt ajoutées au runner Linux
- Extra pip `[gui-qt]` (pyside6) dans pyproject

---

## [3.6.0] - 2026-07-04

### 🏗️ Phase 4 : Refactoring GUI — package gui/, TaskRunner, BaseManager

#### Nouveau package `gui/` (le monolithe passe de 8 926 à ~7 100 lignes)
- `gui/theme.py` : palette Catppuccin Mocha + constantes de mise en page
  (source unique, préalable au thème clair/sombre)
- `gui/config.py` : `GuiConfig`, accès centralisé à `gui_config.json`
  — corrige un bug latent : la sauvegarde des Settings écrasait tout le
  fichier et perdait les clés `paths`/`last_used`
- `gui/task_runner.py` : `TaskRunner`, exécuteur unique des opérations
  longues (R2) — remplace les ~12 blocs « Popen → parsing stdout →
  messagebox → end_operation » copiés-collés (≈ 700 lignes dédupliquées) ;
  streaming des logs, arrêt propre (terminate/kill), callbacks de fin
  exécutés sur le thread UI
- `gui/settings_dialog.py` : SettingsDialog extrait (1 650 lignes)
- `gui/logging_setup.py` : log fichier global `logs/pokemon_gui.log`
  (rotation 1 Mo ×3) — reçoit le panneau de log GUI ET les managers core

#### Thread-safety renforcée
- Nouvelle file de callbacks UI (`_dispatch_ui`) : les threads workers ne
  font plus AUCUN appel Tk, même pas `root.after` (le smoke test a montré
  un `RuntimeError: main thread is not in main loop` possible) ; popups,
  fin d'opération et rafraîchissements passent tous par le poller du
  thread principal

#### core : `BaseManager` (R3)
- `core/base_manager.py` factorise `set_log_callback` / `_log` /
  `set_progress_callback` / `_update_progress`, réimplémentés à
  l'identique dans Workflow/Training/DetectionManager

#### Cross-platform & tests
- `start.sh` : lanceur Linux/macOS (venv-aware), équivalent de START.bat
- 13 nouveaux tests pytest (`tests/test_gui_modules.py`) : GuiConfig,
  TaskRunner (succès/échec/stop/concurrence/subprocess réel), theme,
  logging — **84 tests, 0 échec**
- Smoke test GUI complet exécuté sous display virtuel (xvfb) :
  instanciation, 11 vues, TaskRunner réel, SettingsDialog ✅

#### Décision d'architecture (R8 amendé)
- Les modules de génération restent lancés en sous-processus (isolation
  mémoire/GPU, sortie -u temps réel) mais via le TaskRunner unique ;
  workflow/training/détection continuent d'utiliser les managers en
  direct. Le passage en appels directs pour la génération nécessiterait
  des callbacks de progression dans les modules core (backlog).

---

## [3.5.0] - 2026-07-04

### 🧪 Phase 3 : Tests automatisés, CI et packaging

#### Suite pytest (43 nouveaux tests)
- `tests/conftest.py` : fixtures partagées (mini base de 3 cartes + images
  générées) et exclusion des benchmarks manuels/GPU de la collecte
- `tests/test_core_utils.py` : verrouille les garanties du mapping v3.4.2
  (0-indexé, double clé, cohérence utils/mosaïque/augmentation, régression B2)
- `tests/test_augmentation_pipeline.py` : E2E augmentation sur mini-dataset
  (class_id corrects, exclusion des cartes inconnues, data.yaml ordonné)
- `tests/test_merge_dataset.py` : copy_files, split train/val, extraction de
  classes, data.yaml, fusion complète en arborescence temporaire
- `tests/test_workflow_manager.py` : validation de config, étape MERGE
  critique (régression B5), comptage d'étapes, résumé
- `tests/test_yaml_loading.py` réparé : fixtures hissées au niveau module
  (une classe utilisait la fixture d'une autre) + suppression du `test_main`
  qui relançait pytest récursivement
- **Bilan : 71 tests passent, 1 skip, 0 échec (~3 s)**

#### CI GitHub Actions (`.github/workflows/ci.yml`)
- Job lint : ruff (garde-fou syntaxe + noms non définis) sur tout le dépôt
- Job tests : matrice Ubuntu + Windows × Python 3.11/3.12, cache pip
- Déclenchement sur push, pull request et manuel

#### Packaging (`pyproject.toml`)
- Projet installable (`pip install .`), dépendances regroupées
- Extras : `[training]` (ultralytics), `[excel]` (pandas/openpyxl legacy),
  `[dev]` (pytest, ruff)
- Configuration pytest et ruff centralisée dans pyproject.toml

---

## [3.4.3] - 2026-07-04

### 🧹 Phase 2 : Nettoyage — code mort, doc consolidée, scripts fusionnés

#### Code mort supprimé
- `obsolete/` (12+ fichiers archivés dans l'historique git), `README_old.md`
- `core/augmentation_optimized.py` (imgaug, remplacé par Albumentations en v3.4,
  import cassé depuis le retrait d'imgaug des requirements)
- `core/detection_with_prices.py` + `tests/test_detection_prices.py`
  (remplacés par `core/detection_manager.py`)

#### Scripts consolidés (R7)
- Supprimés : `init_prices_simple.py`, `init_prices_real.py` (codés en dur pour
  l'ancien dataset 8 cartes sv08), `fix_class_mapping.py`, `fix_class_mapping_correct.py`
  (correctifs one-shot rendus inutiles par le mapping unifié de la v3.4.2),
  `create_real_mapping.py`
- `update_prices_yaml_fast.py` devient LE `update_prices_yaml.py` (requêtes parallèles)
- `init_prices.py` : fin de fichier corrompue réparée (le script ne compilait pas),
  chemins résolus via `__file__`
- `create_card_mapping.py` **réécrit générique** : génère `models/card_name_to_id.json`
  depuis `cards_database.yaml` (plus de mapping codé en dur) ; fichier régénéré pour
  la base actuelle (155 cartes xyp au lieu de 8 cartes sv08 périmées)
- Utilitaires `debug_*`, `visualize_*`, `verify_*`, `check_corrupted_images` déplacés
  de `tests/` vers `tools/diagnostics/` (tests/ ne contient plus que de vrais tests)

#### Documentation consolidée
- `docs/new/` promu dans `docs/` : USER_GUIDE, INSTALLATION, FAQ, TECHNICAL_GUIDE,
  API_REFERENCE, ADVANCED (les doublons FEATURES/CHANGELOG périmés de new/ supprimés)
- `docs/migration/` et `CHANGELOG_v3.2.3.md` déplacés vers `docs/archive/`
- README racine : version v3.4, liens cassés corrigés (`README_COMPLET.md`,
  `GUI_V3_GUIDE.md`, `MAINTENANCE_SCRIPTS_REFERENCE.md` n'existaient plus),
  mention imgaug → Albumentations, liens CONTRIBUTING/LICENSE inexistants retirés
- Tous les liens locaux de README.md, docs/README.md et docs/FEATURES.md vérifiés

#### Robustesse
- 23 `except:` nus remplacés par `except Exception:` (core + GUI) — un except nu
  avale aussi KeyboardInterrupt/SystemExit
- `images/.gitkeep` ajouté (le dossier existe désormais dans un clone frais)
- `tests/test_project_integrity.py` mis à jour (7/7) et `SCRIPTS_REFERENCE.py`
  recatalogué

---

## [3.4.2] - 2026-07-04

### 🐛 Phase 1 : Corrections de bugs & fiabilité (plan `.planning/2026-07-04`)

#### Mapping de classes unifié (B3/B4) — ⚠️ important
- `core.utils.load_card_data` est désormais la **source unique de vérité** du mapping
  de classes YOLO : **0-indexé** (standard YOLO, aligné sur data.yaml), chaque carte
  indexée sous deux clés (id complet `xyp_XY05` + numéro court `XY05`)
- Suppression des copies locales divergentes dans `augmentation_albumentations.py`
  (0-indexé) et `mosaic_optimized.py` — l'ancienne version `utils` était 1-indexée
- Le fallback silencieux `class_id = hash(filename) % 1000` est remplacé par un
  avertissement explicite + exclusion de l'image (plus de labels aléatoires)
- Nouvelle fonction `core.utils.build_class_names_list()` (names ordonnés par id)
- L'augmentation écrit à nouveau `output/augmented/data.yaml` (régression de la
  migration v3.4) → `merge_dataset` produit de vrais noms de classes au lieu de `class_N`

#### Autres corrections
- **B1** : `workflow_manager` ajoute `scripts/` au `sys.path` avant `import merge_dataset`
  (le workflow fonctionne maintenant en standalone, pas seulement via le GUI)
- **B2** : `core.utils.load_prices()` sans argument ne plante plus (`TypeError` sur
  `os.path.exists(None)`) — défaut sur `models/cards_database.yaml`
- **B5** : nouvelle étape `WorkflowStep.MERGE` (le merge n'est plus enregistré comme
  MOSAIC) ; `is_success()` compte le merge parmi les étapes critiques
- **B6** : `scripts/merge_dataset.py` résout `config/paths.json` depuis son emplacement
  (`__file__`) et non le répertoire courant
- **B7** : `detection_manager._load_prices` importait `load_prices_from_excel`
  (inexistant) → les prix ne se chargeaient jamais en détection ; charge désormais
  la base YAML via `load_prices()`
- **B8** : `card_mapping.py` cherchait `card_name_to_id.json` à la racine au lieu de
  `models/` (chemin désormais lu depuis `config/paths.json`)
- **Albumentations** : `A.SomeOf(..., n=(3, 6))` plantait à l'init (l'API n'accepte
  qu'un entier) → tirage aléatoire de n∈[3,6] par image via des SomeOf pré-construits ;
  `A.RandomContrast` (supprimé en 2.x) remplacé par son équivalent
  `RandomBrightnessContrast(brightness_limit=0)` ; requirements épinglés
  `albumentations>=1.3.0,<2.0`
- Pattern d'extraction de numéro de carte : support des suffixes `_holoN`

#### GUI : thread-safety (R1)
- `log()` est désormais thread-safe : les messages passent par une `queue.Queue`
  drainée depuis le thread principal (`root.after`) — les threads workers ne touchent
  plus jamais aux widgets Tkinter (source de freezes/crashs aléatoires)
- Nouveaux wrappers `show_info/show_error/show_warning` (popups différées via
  `root.after`) ; les 126 appels `messagebox.*` des workers migrés
- `end_operation`, `update_stats`, `update_all_statistics` se replanifient sur le
  thread principal s'ils sont appelés depuis un worker

#### Tests
- `tests/test_refactoring.py` : le test « NumPy < 2.0 (requis imgaug) » était obsolète
  depuis la migration Albumentations → remplacé par « NumPy >= 1.24 » (5/5 tests OK)

---

## [3.4.1] - 2025-11-28

### 🤖 Jetson Orin AGX 32GB Support

**NEW**: Complete support for NVIDIA Jetson Orin AGX 32GB edge AI platform.

#### New System Profile
- **"🤖 Jetson: Orin AGX 32GB"** added to System Config dropdown
- Optimized defaults for unified memory architecture (32GB shared CPU/GPU)
- Workers reduced to 2 (ARM CPU optimization)
- Disk cache recommended (preserves unified memory)

#### New Training Presets for Jetson

| Preset | Model | ImgSize | Batch | Epochs | Use Case |
|--------|-------|---------|-------|--------|----------|
| ⚡ Fast & Efficient | yolov8n | 416 | 16 | 50 | Standard edge |
| ⚖️ Balanced | yolov8n | 512 | 12 | 50 | Balanced |
| 🎯 High Quality | yolov8s | 640 | 8 | 100 | Max accuracy |
| 🚀 **Jetson Realtime** | yolov8n | 320 | 24 | 30 | **>60 FPS inference** |
| 🤖 **Jetson Optimized** | yolov8n | 480 | 16 | 80 | **Best trade-off Orin** |

#### Export for Jetson
- **New button**: "🚀 Export for Jetson (TensorRT)" in Training view
- Export formats:
  - **TensorRT Engine** (.engine) - Optimal for Jetson, 2-3x speedup
  - **ONNX** (.onnx) - Portable format
  - **TorchScript** (.torchscript) - PyTorch native
- Options:
  - **FP16 (Half precision)** - Recommended for Jetson
  - **INT8 Quantization** - Maximum speed (requires calibration)
  - **Dynamic batch size**

#### UI Updates
- Added 480px image size option (optimal for Jetson)
- Updated Training Presets combobox with Jetson-specific options

---

## [3.4.0] - 2025-11-25

### 🚀 Migration imgaug → Albumentations

**BREAKING CHANGE**: Complete migration from imgaug to Albumentations for image augmentation.

#### Why this change?
- **imgaug** is abandoned since 2020 and blocks NumPy at < 2.0 (deprecated `np.sctypes`)
- **Albumentations** is actively maintained, 30-50% faster, and supports NumPy 2.x

#### Changes Made

**New Files:**
- `core/augmentation_albumentations.py` (495 lines) - New augmentation module with 25 augmentations

**Updated Dependencies (`config/requirements.txt`):**
- `numpy>=1.24.0` (was `numpy<2.0`)
- `opencv-python>=4.8.0` (was `opencv-python<4.10.0`)
- `albumentations>=1.3.0` (replaces `imgaug>=0.4.0`)
- `scipy>=1.11.0` (was `scipy<1.14`)
- `scikit-image>=0.21.0` (was `scikit-image<0.23`)

**Updated Files:**
- `core/__init__.py` - Import augmentation_albumentations as augmentation
- `core/workflow_manager.py` - Reference new augmentation module
- `GUI_v3.1_modern.py` - 2 references updated
- `scripts/workflow_optimized.py` - Reference updated
- `tests/debug_class_map.py` - Import updated
- `tests/debug_augmentation_full.py` - Import updated
- `docs/new/USER_GUIDE.md` - Documentation updated

#### Augmentation Comparison

| Aspect | imgaug (before) | Albumentations (now) |
|--------|-----------------|----------------------|
| Augmentations | 19 | **25** (+6) |
| NumPy support | < 2.0 only | 1.x and 2.x |
| Performance | Baseline | **30-50% faster** |
| Maintenance | Abandoned 2020 | Active (weekly updates) |
| GPU support | Experimental | Stable (via OpenCV-CUDA) |

#### New Exclusive Augmentations
- 🌤️ **RandomShadow** - Realistic shadows
- ☀️ **RandomSunFlare** - Lens flare effects
- 🔍 **CLAHE** - Adaptive histogram equalization
- 📐 **Perspective** - Perspective transformation
- 🌊 **OpticalDistortion** - Lens distortion
- 🔲 **GridDistortion** - Grid-based distortion
- 💨 **MotionBlur** - Motion blur effect
- 📷 **Defocus** - Camera defocus effect
- 📊 **ISONoise** - Camera sensor noise
- 🖼️ **ImageCompression** - JPEG artifacts

**Impact**: Users must run `pip install -r config/requirements.txt` to update dependencies.

---

## [3.3.1] - 2025-11-14

### 📚 Documentation Audit & Cleanup

- **Image References Fixed**: Removed references to 5 missing images that were breaking documentation display
  - Removed: `detection_with_prices.png`, `gui_settings.png`, `example_holographic.png`, `training_metrics.png`, `excel_prices.png`
  - Replaced image sections with descriptive text to maintain documentation completeness
  - Updated `README.md` gallery from 2x2 to 1x2 layout with existing images only
- **Excel → YAML Migration References**: Updated all remaining Excel references to YAML format
  - `excel/cards_with_prices.xlsx` → `models/cards_database.yaml` (10+ occurrences)
  - `excel/generated_extension.xlsx` → Price Database detection
  - `excel/cards_info.xlsx` → `models/cards_database.yaml`
  - Updated in: `README.md`, `HELP.md`, `README_COMPLET.md`, `GUIDE_UTILISATION.md`, `GUI_V3_GUIDE.md`, `docs/features/4_PRICE_SYSTEM.md`
  - Dependencies updated: `openpyxl` references → `pyyaml`
- **Version Standardization**: Unified all documentation to v3.2
  - `HELP.md`: v3.0 → v3.2
  - `FEATURES.md`: v3.1.0 → v3.2.0
  - `GUI_V3_GUIDE.md`: v3.0 → v3.2
  - `README_COMPLET.md`: Multiple v3.1 references → v3.2
  - `GUIDE_UTILISATION.md`: All v3.0 references → v3.2
  - `README_SIMPLE.md`: v3.1 → v3.2
  - Dates updated to November 14, 2025 where appropriate
- **Documentation Verification**: Comprehensive audit of 34+ markdown files
  - All 4 feature docs (`docs/features/*.md`) reviewed and updated
  - Main documentation files (`HELP.md`, `README_COMPLET.md`, `GUIDE_UTILISATION.md`) verified
  - Technical docs (`DEPENDENCIES_MAP.md`, `INTEGRATION_TCGDEX.md`) confirmed accurate
  - 8 Settings tabs correctly documented everywhere
  - 11 functional views properly referenced

**Impact**: Documentation now accurately reflects application state with no broken image links or outdated Excel references. All version numbers consistent at v3.2.

---

## [3.3.0] - 2025-11-14

### 📚 Documentation Refactoring

- **BREAKING CHANGE**: Complete overhaul of the documentation structure for better modularity and maintainability.
- **New `README.md`**: The main `README.md` has been redesigned to be a visually appealing "landing page" that provides a high-level overview and links to detailed documentation.
- **Modular Feature Docs**: The monolithic `docs/README_COMPLET.md` and `docs/FEATURES.md` have been split into smaller, focused files located in the new `docs/features/` directory.
  - `docs/features/1_GUI_OVERVIEW.md`
  - `docs/features/2_DATASET_GENERATION.md`
  - `docs/features/3_TRAINING_AND_DETECTION.md`
  - `docs/features/4_PRICE_SYSTEM.md`
- **Updated `docs/FEATURES.md`**: Now serves as a summary page that links to the new detailed feature documents.
- **Archived Old README**: The previous `README.md` is archived as `README_old.md`.
- **Version Consistency**: Updated all documentation to reflect v3.2 consistently.
- **Image Links Fixed**: Replaced relative image paths with absolute GitHub URLs for proper display.
- **Navigation Links**: Added navigation links between feature documents for easier browsing.
- **Settings Tabs**: Updated references from 6 tabs to 8 tabs (including Advanced & Debug).

---

## [3.2.4] - 2025-11-12

### ⚙️ Settings Enhancement

#### 🐛 Debug Tab (NEW)
- **NEW**: Comprehensive Debug tab in Settings dialog (8th tab)
- **Device Configuration**:
  - Auto (recommended): Automatically detects best device (GPU if available, else CPU)
  - CPU Only: Force CPU processing
  - GPU 0/GPU 1: Manual GPU selection for multi-GPU systems
- **Performance Settings**:
  - Worker count control (1-32 workers with CPU core detection)
  - Cache mode selection: RAM (fastest), Disk (memory-saving), Disabled (minimal footprint)
- **Logging Configuration**:
  - Log level dropdown: ERROR, WARNING, INFO (default), DEBUG, TRACE
  - Save debug logs to file option (`debug_logs/<timestamp>.log`)
- **Advanced Debug Options**:
  - Performance profiling (measures function execution time)
  - Benchmark logging (detailed performance metrics)
  - Multiprocessing debug (detailed parallel processing logs)
  - Memory profiling (tracks memory usage, performance impact)
- **Persistence**: All debug settings saved to `gui_config.json`
- **User quote**: "j'aimerai dans setting un menu debug. ou l on peut activer GPU ou CPU, nombre de worker, choix vobose log (plusieurs mode) et tout ce que j oublie :-D"

#### Documentation Updates
- Updated `README.md`: Settings tabs count (6→8 including Debug)
- Updated `docs/README_COMPLET.md`: Full Debug tab documentation with all features
- Added detailed descriptions for each debug option with warnings

---

## [3.2.3] - 2025-11-12

### 🔧 Configuration System

#### Path Centralization
- **NEW**: All filesystem paths centralized in `config/paths.json`

### 📁 Structure Refactoring

#### Directory Reorganization
- **Simplified structure**: All outputs now under `output/`
  - `backgrounds/augmented/` → `output/backgrounds/`
  - Removed scattered directories for better organization
- **New directories**:
  - `output/backgrounds/`: Fake images with random erasing (replaces `backgrounds/augmented/`)
  - `output/dataset_merged/`: Multi-dataset merging results
- **Dataset structure clarified**:
  - `output/dataset/`: Final YOLO dataset with flat structure (images/ + labels/ + train.txt/val.txt)
  - Merge workflow: `output/augmented/` + `output/mosaics/` → `output/dataset/`

#### Files Updated
- **core/mosaic_optimized.py**: FAKE_DIR → `output/backgrounds/`
- **core/random_erasing.py**: Default output → `output/backgrounds/`
- **GUI_v3.1_modern.py**: Updated all fake images paths (4 occurrences)
- **Planning**: Added `.planning/` system for major changes tracking

#### GUI Improvements
- **Dynamic stats refresh**: Augmentation view now updates every 2 seconds
  - Shows source, holographic, and augmented counts in real-time
- **Settings bandeau**: Changed from gray to blue accent for better visibility

---

## [3.2.1] - 2025-11-11

### 🚀 Performance & UX Improvements

#### Mosaic Generation Ultra-Optimized
- **ProcessPoolExecutor**: Switched from ThreadPoolExecutor to ProcessPoolExecutor
  - True parallel processing (bypasses Python GIL)
  - **30-60x faster** than sequential generation
  - Automatic CPU core detection
- **PNG compression = 0**: Ultra-fast image writing without compression
  - **30-50% faster** file saving
  - Prevents CRC/corruption errors
- **Corrupted image handling**: Robust error recovery
  - Auto-moves bad images to `corrupted/` folder instead of crashing
  - Continues generation without interruption
- **Complete mode fixed**: Now generates all mosaics (unlimited)
  - Removed "Mode ALL non encore optimisé" bug
  - 8000+ images → 1000+ mosaics without limitations

#### GUI Enhancements
- **📂 Open Folder buttons** added to 4 main views:
  - Image Download → `images/`
  - Augmentation → `output/augmented/`
  - Fake Images → `backgrounds/augmented/`
  - Mosaics → `output/mosaics/`
- **New utility method**: `open_folder()` with auto-creation
- **Better button layout**: Horizontal alignment in Mosaics view

#### File Management
- **Prefix system** for mosaics: `L{layout}_B{background}_T{transform}_`
  - No more file overwriting
  - Multiple generation runs coexist (e.g., L1_B0_T0_, L1_B0_T1_)
- **Visualization script updated**: `scripts/visualize_mosaic_bbox.py`
  - Supports new prefix format
  - Filter by prefix (e.g., "L1_B0_T0")

### 🐛 Fixed
- **check_corrupted_images.py**: Fixed for `augmented/` folder location
- **Mode "Complete"**: Removed "all" argument that caused crash
- **Regex pattern**: Updated to match augmented filenames with holo variants

---

## [3.2.0] - 2025-11-11

### 🚀 Major Changes

#### Migration Excel → YAML
- **BREAKING CHANGE**: Card database migrated from Excel to YAML format
- New file: `models/cards_database.yaml` (replaces `excel/cards_info.xlsx`)
- **Benefits**:
  - ~50MB lighter (no pandas/openpyxl required for basic usage)
  - Human-readable and editable format (any text editor)
  - Better Git versioning (clear line-by-line diffs)
  - Faster loading times (~10x faster than Excel)

### ✨ Added

- **YAML Loading** (`core/utils.py`)
  - `load_prices_from_yaml()`: Load card data from YAML
  - `load_prices()`: Auto-detection YAML/Excel with fallback
  - Backward compatible with Excel format

- **Migration Tools** (`scripts/`)
  - `migrate_excel_to_yaml.py`: One-time migration tool for existing users
  - `update_prices_yaml.py`: Update prices in YAML from TCGdex API
  - Updated `init_prices.py` and `init_prices_simple.py` to generate YAML

- **Testing** (`tests/test_yaml_loading.py`)
  - Complete test suite for YAML loading
  - Compatibility tests YAML/Excel
  - Performance benchmarks

- **Documentation**
  - `docs/MIGRATION_EXCEL_TO_YAML.md`: Complete migration guide
  - Updated all docs to reference YAML instead of Excel

### 🔄 Changed

- **GUI** (`GUI_v3.1_modern.py`)
  - Detects YAML instead of Excel
  - `create_sample_excel()` → creates YAML format
  - Updated messages and labels (Excel → YAML)
  - Price display now uses YAML source

- **Core Modules**
  - `core/augmentation.py`: Auto-detect YAML/Excel
  - `core/mosaic.py`: Auto-detect YAML/Excel
  - `core/detection_with_prices.py`: Use `load_prices()` with auto-detection

### 🐛 Fixed

- Excel file locking issues on Windows (YAML doesn't lock)
- Binary diff problems in Git (YAML is text-based)

### 📝 Notes

- **Backward Compatible**: Existing Excel files still work (auto-fallback)
- **Migration**: Run `scripts\run_script.bat migrate_excel_to_yaml`
- **Dependencies**: pandas/openpyxl still in requirements for migration tools only

---

## [3.1.0] - 2025-11-10

### 🎉 Added

#### Card Mapping & Price Detection System
- **Card Mapping Module** (`core/card_mapping.py`)
  - Automatic mapping between class names and TCGdex card IDs
  - Support for `card_name_to_id.json` mapping file
  - Fallback mechanisms for unmapped cards
  
- **Price Detection System** (`core/detection_with_prices.py`)
  - Real-time price display during YOLO detection
  - Integration with Excel price database
  - Support for Cardmarket and TCGPlayer prices
  - Visual price overlays on detected cards

- **Detection Manager Enhancement** (`core/detection_manager.py`)
  - Automatic price loading from Excel
  - Card mapping integration
  - Enhanced detection visualization with pricing info

#### Initialization & Utility Scripts
- **Price Initialization Scripts**
  - `scripts/init_prices.py` - Initialize prices from data.yaml
  - `scripts/init_prices_simple.py` - Simple 8-card training dataset
  - `scripts/init_prices_real.py` - Real card dataset initialization
  
- **Mapping Scripts**
  - `scripts/create_card_mapping.py` - Generate card ID mappings
  - `scripts/create_real_mapping.py` - Create real card mappings
  - `scripts/read_excel_mapping.py` - Excel mapping utilities

- **Debugging & Fixes**
  - `scripts/debug_excel_keys.py` - Debug Excel key issues
  - `scripts/fix_class_mapping.py` - Fix class mapping issues
  - `scripts/fix_class_mapping_correct.py` - Corrected class mapping

#### Testing & Validation Suite
- **Comprehensive Test Files** (moved to `tests/`)
  - `test_annotations.py` - Annotation validation
  - `test_detection_prices.py` - Price detection testing
  - `test_full_chain.py` - End-to-end pipeline testing
  - `test_mapping_debug.py` - Mapping system debugging
  - `test_autobalancer_performance.py` - Auto-balancer benchmarking
  - `test_holographic_performance.py` - Holographic effects testing
  - `test_mosaic_performance.py` - Mosaic generation benchmarking
  
- **Visualization Tools**
  - `visualize_annotations.py` - Visual annotation inspection
  - `visualize_bbox.py` - Bounding box visualization
  
- **Verification Scripts**
  - `verify_data_yaml.py` - Data.yaml validation
  - `verify_detailed.py` - Detailed dataset verification
  - `check_corrupted_images.py` - Image integrity checking

#### Workflow Optimization
- **Optimized Workflow** (`scripts/workflow_optimized.py`)
  - Streamlined pipeline execution
  - Performance improvements
  - Better error handling
  
- **Dataset Management**
  - `scripts/merge_dataset.py` - Dataset merging capabilities
  - Improved dataset organization

### 🔧 Changed

#### Core Module Improvements
- Enhanced `core/augmentation.py` with better error handling
- Improved `core/detection_manager.py` with price integration
- Updated `core/holographic_augmenter.py` for better performance
- Optimized `core/mosaic.py` and `core/mosaic_optimized.py`
- Enhanced `core/random_erasing.py` with new patterns
- Improved `core/training_manager.py` with better logging
- Updated `core/utils.py` with price loading utilities
- Enhanced `core/workflow_manager.py` for better orchestration

#### GUI Enhancements
- Updated `GUI_v3.1_modern.py` with new features
- Enhanced price detection integration in GUI
- Improved configuration management (`gui_config.json`)

### 🗂️ Project Reorganization

#### New Directory Structure
- **`tests/`** - All test and verification scripts
- **`scripts/`** - Utility and initialization scripts
- **`docs/migration/`** - Migration guides and historical documentation
- **`.backups/`** - Project backups (gitignored)

#### Moved Files
- Test files: `test_*.py` → `tests/`
- Visualization: `visualize_*.py` → `tests/`
- Verification: `verify_*.py`, `check_*.py` → `tests/`
- Init scripts: `init_*.py` → `scripts/`
- Utilities: `create_*.py`, `debug_*.py`, `fix_*.py` → `scripts/`
- Workflow: `workflow_optimized.py` → `scripts/`
- Migration docs: `GUIDE_MIGRATION.md`, etc. → `docs/migration/`
- GPU support: `RTX_5070_GPU_SUPPORT.md` → `docs/`

### 🧹 Removed

#### Cleaned Up Files
- Old backup directories (moved to `.backups/`)
- Temporary detection screenshots
- Generated validation reports
- Obsolete dataset exports (COCO, Roboflow)

#### Updated .gitignore
- Added `runs/` - YOLO training outputs
- Added `augmented/`, `augment/` - Generated augmented images
- Added `backup_*/` - Backup directories
- Added `output/holographic/`, `output/yolov8_test/` - Test outputs
- Added `.backups/` - Local backups
- Added `*.cache` - Cache files

### 📚 Documentation

#### New Documentation
- **CHANGELOG.md** - This file, comprehensive project history
- **docs/FEATURES.md** - Detailed feature documentation

#### Updated Documentation
- **README.md** - Updated with new features and organization
- **HELP.md** - Enhanced with price detection and mapping info

### 🐛 Bug Fixes
- Fixed class mapping inconsistencies
- Resolved Excel key matching issues
- Improved error handling in price detection
- Fixed holographic augmentation edge cases

---

## [3.0.0] - 2025-11-08

### Added
- Complete GUI v3.0 with modern interface
- TCGdex API integration for card downloads and prices
- Holographic augmentation effects
- Workflow manager with custom pipelines
- YOLOv8/YOLO11 training integration
- Live detection (webcam/video/image)
- Multi-format dataset export (COCO, VOC, TFRecord, Roboflow)
- Comprehensive settings system with 6 tabs
- Auto-balancing for dataset optimization

### Changed
- Complete UI redesign with modern aesthetics
- Improved mosaic generation with 3 modes
- Enhanced augmentation with 22+ transformation types
- Better error handling and logging

---

## [2.0.0] - 2025-10

### Added
- Initial YOLO pipeline implementation
- Basic augmentation system
- Mosaic generation
- TCGdex API support

### Changed
- Major architecture refactoring
- Improved code organization

---

## [1.0.0] - Initial Release

### Added
- Basic dataset generation
- Simple augmentation
- Command-line interface

---

## 🔗 Links

- **Repository**: https://github.com/lo26lo/pok
- **Documentation**: [HELP.md](HELP.md)
- **Features**: [docs/FEATURES.md](docs/FEATURES.md)
- **TCGdex Integration**: [docs/INTEGRATION_TCGDEX.md](docs/INTEGRATION_TCGDEX.md)

---

## 📝 Notes

### Version Numbering
- **Major** (X.0.0): Breaking changes, major features
- **Minor** (x.X.0): New features, backwards compatible
- **Patch** (x.x.X): Bug fixes, minor improvements

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities
