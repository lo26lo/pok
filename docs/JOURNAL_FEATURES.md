# 📓 Journal des Features — Suivi & Reprise

> **But de ce document** : suivre l'avancement des 10 nouvelles features validées le 2026-07-12,
> et permettre à n'importe qui (humain ou session Claude) de **reprendre le travail exactement là où il s'est arrêté**.
>
> **Branche de développement** : `claude/new-feature-proposals-v4x2m3`
>
> **Règles de tenue du journal** :
> 1. Chaque session de travail ajoute une entrée datée dans le [Journal de bord](#-journal-de-bord) (la plus récente en haut).
> 2. À chaque avancée, mettre à jour le statut dans le [Tableau de suivi](#-tableau-de-suivi) et la checklist de la feature concernée.
> 3. Avant de terminer une session : remplir la section [🔄 Point de reprise](#-point-de-reprise) (ce qui est en cours, prochaine étape concrète, pièges connus).
> 4. Un commit par étape logique, préfixé par l'ID de la feature : `feat(F01): ...`, `test(F04): ...`, etc.

---

## 📊 Tableau de suivi

Statuts : ⬜ À faire · 🔵 En design · 🟡 En cours · 🟢 Terminé · ⏸️ En pause · ❌ Abandonné

| ID | Feature | Catégorie | Priorité | Statut | Avancement |
|:---|:--------|:----------|:--------:|:------:|:----------:|
| F01 | Identification fine de la carte (embeddings + FAISS) | Détection | ⭐ Haute | 🟢 | 100 % |
| F02 | Estimation de l'état de la carte (grading) | Détection | Basse | 🟢 | 100 % |
| F03 | Mode « scan de collection » (inventaire + valeur) | Détection | ⭐ Haute | 🟢 | 100 % |
| F04 | Backgrounds réalistes automatiques | Dataset | ⭐ Haute | 🟡 | 90 % |
| F05 | Occlusions réalistes (éventails, sleeves, mains) | Dataset | Moyenne | 🟢 | 100 % |
| F06 | Prévisualisation live des augmentations (GUI) | Dataset | Moyenne | 🟢 | 100 % |
| F07 | Onglet « Évaluation » (PR, confusion, pires prédictions) | Training | Moyenne | 🟢 | 100 % |
| F08 | Set de validation « réel » annoté + métrique dédiée | Training | Moyenne | 🟡 | 80 % |
| F09 | Historique et alertes de prix (SQLite + sparklines) | Prix | Basse | 🟢 | 100 % |
| F10 | Cache API hors-ligne (snapshot des prix) | Prix | Basse | 🟢 | 100 % |

### Ordre de réalisation prévu

Les features sont regroupées en vagues pour maximiser la réutilisation :

1. **Vague 1 — Qualité du modèle** : F04 → F05 → F06 (la géné de dataset est le socle de tout le reste)
2. **Vague 2 — Mesure** : F08 → F07 (savoir si la vague 1 a réellement amélioré le transfert au réel)
3. **Vague 3 — Valeur produit** : F01 → F03 (identification exacte, puis inventaire qui s'appuie dessus)
4. **Vague 4 — Confort** : F10 → F09 → F02

> Cet ordre est indicatif : il peut être modifié, mais noter la raison dans le journal de bord.

---

## 🔄 Point de reprise

> **⚠️ Section à mettre à jour EN FIN DE CHAQUE SESSION.** C'est la première chose à lire en reprenant le travail.

- **Dernière session** : 2026-07-12 (session 7)
- **Feature en cours** : aucune — **les 10 features (F01–F10) sont terminées**, les 4 vagues sont complètes. Suite : 299 tests passés, 0 échec.
- **Prochaine étape concrète** : plus de développement planifié dans ce cycle. Pistes du backlog (par fiche) : photos réelles F08 (action utilisateur, débloque la mesure d'amélioration F04 et un classifieur de coins F02), grading agrégé dans le scan F03, alertes mail/webhook F09, relevé de prix périodique F10, doigts plus élaborés F05, branchement intensité/catégories dans la génération F06.
- **⚠️ À valider en conditions réelles (réseau bloqué dans l'environnement de dev)** :
  - premier préchargement : `python tools/preload_prices.py --set sv08` (flux API réel) ;
  - benchmark F01 rejouable sur vos sets : `python tools/benchmark_card_embeddings.py --images images` ;
  - ouverture des fenêtres « 💹 Price History » et des nouvelles cases de la vue Detection (pas de smoke test xvfb possible ici — python3.11-tk intéléchargeable).
- **En attente de décision utilisateur** :
  - 📸 **déposer des photos de vraies cartes dans `datasets/real_val/images/`** (suivre le README), puis `python tools/preannotate_real_val.py` et corriger les labels (F08).
  - 🎴 Optionnel : reconstruire l'index d'identification sur VOS sets téléchargés : `python tools/build_card_index.py` (l'index n'est pas committé ; le modèle ONNX l'est).
- **Pièges / notes connues** :
  - `core/mosaic_optimized.py` : `_process_single_group` tourne dans des sous-processus (`ProcessPoolExecutor`) — tout nouvel état doit être picklable et passé via le tuple `args`.
  - Le combobox « Background Mode » de la GUI (`gui/settings_dialog.py`) stocke des chaînes `"3 - Realistic (Procedural)"` dans un `IntVar` — comportement hérité, ne pas « corriger » isolément.
  - Les effets caméra sont appliqués UNIQUEMENT en mode 3, après compositing (sinon double vignettage si on les mettait aussi dans le fond).
  - `cv2.dnn` (OpenCV 5) **ignore le nom de couche passé à `forward()`** pour ce graphe ONNX : impossible d'extraire la couche pool du modèle complet — d'où le modèle TRONQUÉ livré dans `models/mobilenetv2_embeddings.onnx` (la troncature est refaite par `--download-model` si le package `onnx` est installé ; sinon logits 1000-d, ~91 % top-1 au lieu de 98 %).
  - L'index et les requêtes doivent partager le même embedder : `CardIdentifier` lit la méthode dans `meta.json` de l'index ; si l'ONNX change, reconstruire l'index.
  - `backgrounds/original/` contient 245 vraies cartes TCGdex (swsh7 + sv08) committées — utilisées par le benchmark et les tests de précision F01.

---

## 📋 Fiches features

Chaque fiche contient le périmètre, les fichiers concernés, la checklist d'implémentation et les critères d'acceptation.
Cocher les cases au fur et à mesure ; ajouter des sous-tâches si besoin.

---

### F01 — Identification fine de la carte (2ᵉ étage de pipeline)

**Objectif** : après la localisation YOLO, identifier *quelle* carte exacte est détectée (set + numéro),
même hors des classes entraînées, via un index d'embeddings construit sur les images TCGdex déjà téléchargées.

**Approche pressentie** : crop de la bbox → embedding (CLIP ou petit CNN) → recherche k-NN dans un index FAISS
construit à partir de `images/` (base TCGdex). Plus besoin de réentraîner YOLO pour chaque nouveau set.

**Fichiers/Modules concernés** : `core/detection_manager.py`, `core/tcgdex_api.py`, `core/card_mapping.py`, nouveau `core/card_identifier.py`

- [x] Design : **CNN léger retenu** — MobileNetV2 (features global-pool 1280-d) via `cv2.dnn`, zéro dépendance Python ajoutée ; benchmark sur les 245 cartes réelles du dépôt (requêtes webcam simulées) : **dnn 98,4 % top-1 / 100 % top-5 / 6,6 ms** vs classic (descripteur Lab+gradients) 74,2 % / 1,5 ms. CLIP non retenu (poids intéléchargeables dans cet environnement, latence CPU défavorable, inutile pour du quasi-doublon)
- [x] Script de construction de l'index : `tools/build_card_index.py` (scan `images/`, dédoublonnage multi-langues, `--check`, `--download-model`) → `models/card_index/` (embeddings.npy + cards.json + meta.json)
- [x] `core/card_identifier.py` : API `identify(crop) -> IdentificationResult` (card_id, score, top_k) ; FAISS optionnel avec fallback numpy ; références moyennées sur 3 vues (natif/300px/300px flou : +11 pts de top-1)
- [x] Intégration `DetectionManager` : `identify_cards` + `identify_min_score` dans la config, chargement best-effort (jamais bloquant), champs `card_id`/`exact_name`/`identify_score` sur `Detection`, CLI `--identify`
- [x] Affichage GUI : case « 🎴 Identify Cards » (vue Detection) ; overlay « Skiploom [swsh7 003] » ; prix cherché directement par card_id (plus fiable que le mapping par nom de classe)
- [x] Tests : 33 tests (`tests/test_card_identifier.py`) dont précision top-1 ≥ 90 % / top-5 ≥ 95 % sur 40 cartes réelles perturbées — suite : 205 passés, 0 échec
- [x] Docs : section dans `docs/FEATURES.md` + entrée CHANGELOG

**Critères d'acceptation** : top-1 ≥ 90 % sur cartes bien cadrées ✅ (98,4 % mesuré sur requêtes dégradées) ; latence < 50 ms par carte sur CPU ✅ (~7 ms embed + <0,1 ms recherche) ; fonctionne sur un set jamais vu par YOLO ✅ (l'index est indépendant des classes YOLO — testé avec un YOLO nu sur l'index swsh7).

**Notes de session** :
- 2026-07-12 : implémentation complète. Le modèle ONNX **tronqué à la couche pool** est committé (`models/mobilenetv2_embeddings.onnx`, 9 Mo, Apache-2.0) car `cv2.dnn` (OpenCV 5) ne permet pas d'extraire une couche intermédiaire du modèle complet (les logits 1000-d donnent 91 % au lieu de 98 %). L'index n'est PAS committé : `python tools/build_card_index.py` le construit en ~30 s pour 245 cartes. Backlog : cache d'identification par tracking inter-frames (utile pour F03), seuil `identify_min_score` réglable dans la GUI.

---

### F02 — Estimation de l'état de la carte (grading)

**Objectif** : estimer l'état (centrage, coins, rayures de surface) depuis la webcam et pondérer le prix affiché (Near Mint vs Played).

**Fichiers/Modules concernés** : `core/detection_manager.py`, nouveau `core/card_grader.py`

- [x] Design : métriques retenues = **centrage** (fiable) + **coins blanchis** (heuristique assumée) ; **rayures écartées en v1** (résolution webcam insuffisante pour être fiable — décision actée)
- [x] Détection du centrage : profils de gradients moyennés sur le tiers central, **premier edge significatif depuis l'extérieur** dans la bande [2 %, 22 %] de chaque bord (= transition bordure→cadre, robuste aux edges du texte) ; ratios G/(G+D) et H/(H+B) — précision mesurée ±3 %
- [x] Coins abîmés : blanchiment = pixels très clairs ET désaturés (signature commune aux bordures jaunes/argent/noires) ; arrondi de la carte masqué (coin de crop serré = fond) ; analyse restreinte à la bande de bordure ; neutre si bordure blanche (vieux sets, indétectable)
- [x] Pondération du prix : barème NM/EX/GD/PL → facteurs 1.0/0.85/0.70/0.50 (score global = 60 % centrage + 40 % coins), prix de l'overlay multiplié par le facteur
- [x] Affichage GUI : badge d'état dans le label de détection (« ... [NM] »), case « 🔍 Grade Cards », CLI `--grade`
- [x] Tests (22, `tests/test_card_grader.py`) + docs

**Critères d'acceptation** : centrage mesuré à ±5 % ✅ (±3 % mesuré sur 4 configurations synthétiques paramétrées, ~50/50 confirmé sur scans TCGdex parfaits) ; l'estimation ne bloque jamais la détection ✅ (`grade()` ne lève jamais, testé sur crops dégénérés/uniformes).

**Notes de session** :
- 2026-07-12 : implémentation complète, ~3 ms par carte. Limites connues de l'heuristique coins : éléments graphiques blancs près des coins (ex. cartes V) peuvent baisser le score, et le centrage n'a pas de sens sur les full-arts sans cadre — badge à lire comme indicatif. Backlog : petit classifieur de coins si des photos réelles annotées deviennent disponibles (F08), grading agrégé dans le scan de collection (pondérer la valeur de l'inventaire).

---

### F03 — Mode « scan de collection »

**Objectif** : session de détection continue qui déduplique les cartes vues, construit un inventaire
(CSV/Excel — réutiliser `excel/`) avec valeur totale de la collection en fin de session.

**Dépend de** : F01 (identification exacte) fortement recommandé ; possible en mode dégradé (classes YOLO seules) avant.

**Fichiers/Modules concernés** : `core/detection_manager.py`, `excel/`, nouveau `core/collection_scanner.py`, GUI (nouvelle vue ou mode dans la vue Détection)

- [x] Design : confirmation après **min_hits frames** (défaut 3, pas forcément consécutives) puis déduplication par clé pour toute la session — clé = `card_id` F01, ou `yolo:<classe>` en mode dégradé ; quantité = max de détections simultanées de la même clé dans une frame
- [x] `core/collection_scanner.py` : `observe_frame(detections)` (duck-typé sur `Detection`), inventaire trié par première apparition, `summary()` (cartes uniques, exemplaires, valeur min-max, cartes sans prix, durée), `reset()`
- [x] Prix par carte : base locale `models/cards_database.yaml` via `load_prices()` (aucun appel réseau) ; en mode dégradé, mapping classe→card_id réutilisé
- [x] Export CSV + Excel : `output/collection_scans/scan_<timestamp>.{csv,xlsx}`, Excel avec ligne de totaux en gras (openpyxl optionnel, CSV toujours disponible)
- [x] GUI : bouton « 🧺 START COLLECTION SCAN » (vue Detection, identification F01 forcée), compteur live sur l'overlay webcam, récap de fin (cartes, valeur, durée, chemins) ; CLI `--scan`
- [x] Tests (22, `tests/test_collection_scanner.py`) + docs (FEATURES.md, CHANGELOG)

**Critères d'acceptation** : une même carte présentée 10 s n'apparaît qu'une fois ✅ (testé sur 300 frames, y compris départ/retour de la carte) ; export Excel ouvrable avec totaux corrects ✅ (relu par openpyxl dans les tests, totaux quantité/valeur vérifiés).

**Notes de session** :
- 2026-07-12 : implémentation complète, dans la même session que F01 (le scanner s'appuie sur `CardIdentifier`). Le scanner est découplé de la caméra (API `observe_frame`) : testable sans webcam et réutilisable pour un futur scan vidéo/dossier. Backlog : bouton « ouvrir le dossier des scans » dans la GUI, détection de doublons inter-sessions (F09 pourra s'appuyer sur l'inventaire).

---

### F04 — Backgrounds réalistes automatiques

**Objectif** : remplacer/compléter `tools/generate_fake_backgrounds.py` par des fonds réalistes
(tapis de jeu, bois, classeurs, mains) + placement avec ombres portées et perspective.
Levier n°1 attendu pour réduire l'écart sim-to-real.

**Fichiers/Modules concernés** : `tools/generate_fake_backgrounds.py`, `core/mosaic_optimized.py`, `backgrounds/`

- [x] Design : **génération procédurale** retenue (vs téléchargement) — pas de problème de licence, pas de réseau, variété infinie, reproductible via seed
- [x] Pipeline de génération des fonds : `core/background_generator.py`, 5 catégories (`wood`, `playmat`, `binder`, `fabric`, `desk`) — la catégorie « main » est reportée sur F05 (overlays de doigts)
- [x] Ombres portées sous les cartes : `add_drop_shadow()` (masque alpha flouté, offset/blur/strength aléatoires par carte)
- [x] Perspective : déjà couverte par `transform_mode 1` (`rotate_image_3d`) — rien à ajouter
- [x] Variations d'éclairage globales : `apply_camera_effects()` (température, exposition, éclairage directionnel, vignettage)
- [x] Intégration pipeline : **background_mode 3** dans `core/mosaic_optimized.py` (fond à la volée + ombres + effets caméra) ; option « 3 - Realistic (Procedural) » dans la GUI
- [x] Tests visuels : galerie via `tools/generate_realistic_backgrounds.py --gallery` ; 17 tests unitaires (`tests/test_background_generator.py`)
- [x] Docs (`FEATURES.md`) + CHANGELOG (`[Unreleased]`)
- [ ] Amélioration mesurable sur le set réel → **bloqué par F08** (le set réel n'existe pas encore)

**Critères d'acceptation** : galerie d'échantillons jugée « crédible » ✅ ; annotations toujours valides après perspective ✅ (effets purement photométriques) ; amélioration mesurable sur le set réel (cf. F08) ⏳.

**Notes de session** :
- 2026-07-12 : implémentation complète. Le mode 3 génère les fonds à la volée dans chaque sous-processus (aucun fichier requis). `tools/generate_realistic_backgrounds.py` sert à l'inspection visuelle et à la pré-génération optionnelle. Suite de tests : 96 passés, 0 échec.

---

### F05 — Occlusions réalistes

**Objectif** : générer des cartes en éventail, partiellement recouvertes, sous sleeves/toploaders (reflets plastiques),
pour que le modèle gère les mains de cartes réelles.

**Dépend de** : F04 (partage le même pipeline de placement).

**Fichiers/Modules concernés** : `core/mosaic_optimized.py`, `core/holographic_augmenter_optimized.py` (reflets)

- [x] Design : taxonomie retenue = éventail (pivot « poignet », arc de cercle), chevauchement contrôlé par l'ordre d'empilement, sleeve mate ou brillante (50 % des cartes), doigts procéduraux (2-4, 6 teintes de peau)
- [x] Placement en éventail : `fan_layout()` + `_compose_fan_group()` (layout_mode 4) — bbox = étendue complète de la carte clippée au canvas (convention YOLO amodale), cartes < 25 % visibles jamais annotées (`compute_visible_fractions`, buffer d'étiquettes 1/4)
- [x] Effet sleeve/toploader : `apply_sleeve()` (voile laiteux, bande spéculaire diagonale ou rendu mat, liseré) — dimensions inchangées donc annotations valides
- [x] Doigts/mains : **procéduraux** (`add_fingers`), pas d'assets PNG — cohérent avec le choix « tout procédural » de F04
- [x] Paramètres : layout_mode 4 exposé en CLI (`core/mosaic_optimized.py 4 3 0`) et dans la GUI (« 4 - Fan / Hand (Occlusions) »)
- [x] Tests : 15 tests (`tests/test_occlusion_effects.py`) dont visibilité (recouvrement total/partiel/hors-canvas) et intégration layout 4 — suite : 111 passés, 0 échec

**Critères d'acceptation** : bboxes des cartes partiellement visibles correctes ✅ (vérifié visuellement + tests bornes [0,1]) ; pas de carte quasi masquée annotée ✅ (seuil MIN_VISIBLE_FRACTION = 0.25, testé).

**Notes de session** :
- 2026-07-12 : implémentation complète. Combiner layout 4 + background_mode 3 donne le rendu le plus réaliste (ombres + effets caméra inclus). Amélioration possible en backlog : doigts plus élaborés (pouce, ongle) et éventails tenus depuis le bord du canvas.

---

### F06 — Prévisualisation live des augmentations (GUI)

**Objectif** : un onglet GUI qui applique le pipeline Albumentations à une carte échantillon en temps réel
quand on modifie les paramètres, sans lancer une génération complète.

**Fichiers/Modules concernés** : `core/augmentation_albumentations.py`, `gui/` (nouvelle vue), `GUI_v3.1_modern.py`

- [x] Design : sliders intensité globale (0.1×–2×) + nb de transformations (0 = aléatoire 3-6) + 6 cases catégories ; 1 carte, 6 variantes
- [x] Refactor : `build_transform_pool(intensity, categories)` + `preview_augmentations()` dans `core/augmentation_albumentations.py` — le pipeline de production (intensity=1.0) est inchangé, verrouillé par test
- [x] Vue GUI : `gui/augmentation_preview.py` (Toplevel), choix de carte / carte aléatoire, grille original + 6 variantes, bouton Regenerate, debounce 350 ms, rendu en thread + file pollée (thread-safe v3.6)
- [x] Application des paramètres : `get_params()` expose `{intensity, n_transforms, categories}` réutilisables (le branchement vers la config de génération viendra quand la génération acceptera ces paramètres — cf. note)
- [x] Tests : 17 tests (pool, preview, helpers purs sans Tk) + smoke test xvfb complet avec capture d'écran

**Critères d'acceptation** : rafraîchissement < 500 ms pour 6 aperçus ✅ (thread + debounce, UI jamais bloquée) ; aucun sous-processus lancé ✅ ; paramètres exposés via `get_params()` ✅.

**Notes de session** :
- 2026-07-12 : le smoke test xvfb a attrapé un `RuntimeError: main thread is not in main loop` (appel `after()` depuis le worker) — corrigé avec le pattern v3.6 (queue + poller). Le module est import-safe sans tkinter (helpers testables headless). Backlog : passer `intensity/categories` au pipeline de génération complet (aujourd'hui la génération utilise toujours intensity=1.0, valeurs historiques).

---

### F07 — Onglet « Évaluation »

**Objectif** : courbes PR, matrice de confusion, galerie des pires prédictions dans la GUI,
avec comparaison entre deux runs d'entraînement.

**Fichiers/Modules concernés** : `core/training_manager.py`, `gui/` (nouvelle vue), sorties Ultralytics dans `output/`/`runs/`

- [x] Design : **réutilisation des artefacts Ultralytics** (results.csv parsé, PNGs affichés tels quels) — pas de matplotlib embarqué, zéro dépendance ajoutée
- [x] Parsing des runs : `core/run_analyzer.py` (list_runs, run_summary au meilleur epoch mAP50-95, args.yaml, real_mAP F08 rattaché au best.pt du run)
- [x] Affichage courbes : boutons d'artefacts (results, confusion, confusion norm., PR/F1/P/R, labels, val_batch*_pred) avec redimensionnement à la volée
- [x] Galerie « pires prédictions » : score d'erreur par image (IoU 0.5, appariement glouton — manqués / faux positifs / mauvaise classe), planche contact annotée (GT vert, préd. rouge) ; source = set réel F08 si prêt, sinon val synthétique (val.txt du dataset fusionné)
- [x] Comparaison A/B : deltas des métriques communes avec flèches ▲▼
- [x] Tests : 19 tests (parsing, scoring IoU/appariement, helpers de vue) + smoke test xvfb avec capture

**Critères d'acceptation** : tout run existant visualisable sans relancer d'entraînement ✅ ; comparaison A/B lisible ✅ (validée visuellement).

**Notes de session** :
- 2026-07-12 : vue déléguée à `gui/evaluation_view.py` (le monolithe ne gagne que ~15 lignes : bouton sidebar + dispatch + fallback). L'inférence des pires prédictions tourne en thread avec la file pollée (pattern v3.6). La galerie affichera automatiquement le set réel dès que F08 sera peuplé.

---

### F08 — Set de validation « réel » annoté

**Objectif** : un mini-set de photos de vraies cartes, annoté, séparé du dataset synthétique,
avec une métrique dédiée pour mesurer le vrai transfert au monde réel.

**Fichiers/Modules concernés** : `core/training_manager.py`, `core/dataset_validator.py`, nouveau dossier `datasets/real_val/` (ou équivalent)

- [x] Design : protocole de capture reproductible (30-100 photos, 2+ appareils dont la webcam de détection, 3 éclairages, 4 surfaces, dispositions à plat/éventail/sleeve, angles 0-45°) — `datasets/real_val/README.md`
- [x] Structure : `datasets/real_val/{images,labels}` (format YOLO, fichier vide = négatif), `check_real_val_set()` + CLI `python core/real_validation.py --check`
- [x] Pré-annotation assistée : `tools/preannotate_real_val.py` (prédictions du modèle courant comme brouillon, correction manuelle obligatoire)
- [x] Script d'évaluation : `evaluate_real_map()` → real_mAP50 / real_mAP50-95 / precision / recall, rapport JSON avec historique (`output/real_val_report.json`)
- [x] **Garde anti-fuite** : hash MD5 du set réel contre les 4 dossiers d'entraînement — évaluation refusée si leak
- [x] Intégration fin d'entraînement : `auto_evaluate_if_available()` dans `TrainingManager.train()` (jamais bloquant) ; l'onglet Évaluation viendra avec F07
- [ ] **Photos réelles à fournir par l'utilisateur** (le set est vide : infrastructure prête, métrique inerte tant qu'il n'y a pas de photos annotées)

**Critères d'acceptation** : `real_mAP` calculé et affiché après chaque entraînement ✅ (dès que le set est peuplé) ; le set réel n'entre JAMAIS dans le train ✅ (garde MD5 testée).

**Notes de session** :
- 2026-07-12 : infrastructure complète et testée (20 tests). Reste 20 % : peupler le set (action utilisateur — suivre le protocole du README, puis `tools/preannotate_real_val.py` et correction manuelle). Une fois peuplé, relancer un entraînement affichera real_mAP automatiquement.

---

### F09 — Historique et alertes de prix

**Objectif** : stocker les prix relevés en SQLite, afficher des sparklines d'évolution,
notifier quand une carte de l'inventaire dépasse un seuil.

**Dépend de** : F10 (même couche de persistance des prix) ; F03 pour la notion d'inventaire.

**Fichiers/Modules concernés** : `core/price_cache.py` (couche F10 réutilisée — pas de `price_store.py` séparé), `gui/price_history_view.py`, GUI

- [x] Design : schéma = table `price_snapshots` de F10 (carte, source, prix, devise, timestamp — append-only) + table `price_alerts` (seuil, direction, armement) ; fréquence de relevé = chaque préchargement (explicite, pas de démon)
- [x] Écriture à chaque relevé + requêtes d'historique : déjà en place depuis F10 (`put()` append-only, `history()` antichronologique)
- [x] Sparklines dans la GUI : fenêtre « 💹 Price History » (canvas Tk pur — cohérent avec la décision F07 « pas de matplotlib »), sélecteur de carte, synthèse actuel/min/max/tendance
- [x] Alertes de seuil : `set_alert/remove_alert/list_alerts/check_alerts` — déclenchement fiable sans spam (désarmée au déclenchement, réarmée quand la condition redevient fausse) ; notification GUI + log après chaque préchargement ; mail/webhook laissé en extension
- [x] Tests (23, `tests/test_price_alerts.py`) + docs

**Critères d'acceptation** : historique persistant entre sessions ✅ (SQLite, testé sur réouverture) ; alerte déclenchée de façon fiable au franchissement ✅ (cycle armée→déclenchée→désarmée→réarmée testé dans les deux directions).

**Notes de session** :
- 2026-07-12 : implémentation complète sur la couche F10 comme prévu au point de reprise. Pas de smoke test xvfb possible dans cet environnement (python3.11-tk intéléchargeable, dépôt apt bloqué) : la fenêtre suit le pattern F06 (import-safe, helpers purs testés headless) — à vérifier visuellement à la première ouverture. Backlog : alertes mail/webhook, relevé périodique automatique.

---

### F10 — Cache API hors-ligne

**Objectif** : snapshot local des prix pour utiliser la détection sans réseau.

**Fichiers/Modules concernés** : `core/tcgdex_api.py`, intégrations prix existantes, nouveau cache (fichier ou SQLite partagé avec F09)

- [x] Design : **SQLite append-only** (`models/price_cache.db`, table `price_snapshots` horodatée = déjà l'historique pour F09) ; TTL 24 h qui pilote le *rafraîchissement*, pas la validité (hors-ligne, l'entrée périmée est servie avec sa date) ; taille bornée par `purge(keep_per_card)`
- [x] Couche transparente : `TCGdexAPI(cache=...)` + `get_card_prices()` — cache frais → API (snapshot enregistré au passage) → cache périmé en mode avion ; `load_prices_with_cache()` fusionne YAML + cache et remplace `load_prices()` dans la détection et le scanner F03
- [x] Préchargement : `tools/preload_prices.py` (`--set sv08`, `--database`, `--inventory scan.csv`, `--check`, `--purge N`) + bouton GUI « ⬇ Preload Prices »
- [x] Mode hors-ligne explicite : indicateur GUI « 💾 N prix, snapshot du JJ/MM » (vue Detection), log « 📴 Hors-ligne: prix du JJ/MM » à chaque service d'une entrée périmée, `price_date` exposée dans les prix fusionnés
- [x] Tests (27, `tests/test_price_cache.py`) : hit/miss, expiration TTL, mode avion (entrée périmée servie, carte inconnue → None), historique/purge, fusion YAML+cache, variantes de padding, sources de préchargement + docs

**Critères d'acceptation** : détection + affichage prix 100 % fonctionnels sans réseau après préchargement ✅ (la couche fusionnée est purement locale ; testé avec API mockée coupée) ; date du snapshot visible ✅ (indicateur GUI + date par entrée).

**Notes de session** :
- 2026-07-12 : implémentation complète. Identifiants normalisés entre TCGdex (`swsh7-3`) et le projet (`swsh7_003`) — le padding du localId varie selon les sets, `tcgdex_id_candidates()` essaie les deux formes. Le préchargement réseau n'a pas pu être exécuté ici (egress bloqué vers api.tcgdex.net) : flux validé avec API mockée ; à valider en conditions réelles au premier `--set`. Backlog : rafraîchissement automatique périodique (cron GUI) une fois F09 en place.

---

## 📆 Journal de bord

> Entrées antéchronologiques (la plus récente en haut).
> Format : date, auteur/session, features touchées, ce qui a été fait, décisions prises.

### 2026-07-12 (session 7, fin) — F09 et F02 implémentées : les 4 vagues sont complètes 🎉
- **Features** : F09, F02
- **Fait** :
  - F09 : table `price_alerts` (SQLite, même base que F10), cycle fiable armée→déclenchée→désarmée→réarmée, check en fin de préchargement (log + notification GUI), fenêtre « 💹 Price History » (sparkline canvas Tk pur, synthèse, gestion des alertes). 23 tests.
  - F02 : `core/card_grader.py` — centrage par premier edge significatif depuis l'extérieur (±3 % mesuré), coins blanchis (clairs ET désaturés, arrondi masqué, bande de bordure, neutre sur bordure blanche), barème NM/EX/GD/PL avec prix pondéré, badge dans l'overlay, case GUI + CLI `--grade`. 22 tests.
  - Suite finale : 299 passés / 0 échec ; ruff OK.
- **Décisions** :
  - F09 sur la couche F10 (pas de `price_store.py` séparé) ; sparklines en canvas Tk pur (cohérent avec « pas de matplotlib » de F07).
  - F02 : rayures écartées en v1 (webcam insuffisante) ; heuristique coins assumée comme indicative (limites : graphismes blancs près des coins, full-arts sans cadre).
- **Bilan de la session 7** : F01, F03, F10, F09, F02 — 5 features, 127 tests ajoutés (172 → 299), et le plan des 10 features validé le 2026-07-12 est entièrement réalisé.

### 2026-07-12 (session 7, suite) — F10 implémentée, vague 4 entamée
- **Features** : F10
- **Fait** :
  - `core/price_cache.py` : PriceCache SQLite append-only (get/put/latest_all/history/stats/purge), normalisation d'identifiants TCGdex↔projet, `load_prices_with_cache()`, `snapshot_status()`, `preload_prices()` (ThreadPool).
  - `TCGdexAPI(cache=...)` + `get_card_prices()` (cache frais → API → périmé hors-ligne).
  - Détection et scanner F03 branchés sur la fusion YAML+cache.
  - `tools/preload_prices.py` (set / base / inventaire / check / purge) ; GUI : indicateur snapshot + bouton Preload.
  - 27 tests ; suite 254 passés / 0 échec.
- **Décisions** :
  - Le TTL ne rend jamais une entrée inutilisable : il déclenche seulement le rafraîchissement réseau — hors-ligne, on sert le dernier snapshot avec sa date (critère « prix du JJ/MM »).
  - Table append-only = historique de prix : F09 s'appuiera sur `history()` au lieu d'un nouveau `price_store.py`.
  - Le cache GAGNE sur le YAML dans la fusion (préchargement explicite = plus récent), mais un snapshot sans prix n'efface pas un prix YAML.
- **Prochaine étape** : F09 (sparklines + alertes sur la même table).

### 2026-07-12 (session 7, suite) — F03 implémentée, vague 3 complète
- **Features** : F03
- **Fait** :
  - `core/collection_scanner.py` : confirmation après min_hits frames, dédup par card_id (ou classe YOLO en dégradé), quantité par détections simultanées, prix locaux, agrégats, exports CSV/Excel avec totaux.
  - `DetectionManager.detect_webcam(scanner=...)` : détections par frame vers le scanner, compteur live sur l'overlay, log des confirmations, CLI `--scan`.
  - GUI : bouton « 🧺 START COLLECTION SCAN » + récap de fin de session.
  - 22 tests ; suite 227 passés / 0 échec.
- **Décisions** :
  - Scanner découplé de la caméra (`observe_frame`) : testable sans webcam, réutilisable hors GUI.
  - Les hits de confirmation n'ont pas besoin d'être consécutifs (robuste aux frames ratées) ; une carte confirmée reste dédupliquée même si elle sort du champ et revient.
  - Prix uniquement depuis la base locale (pas d'appel API pendant le scan — F10 apportera le préchargement).
- **Prochaine étape** : vague 4 — F10 (cache API hors-ligne).

### 2026-07-12 (session 7) — F01 implémentée, vague 3 entamée
- **Features** : F01
- **Fait** :
  - Benchmark d'embedding sur les 245 cartes réelles committées dans `backgrounds/original/` (requêtes webcam simulées : perspective, rotation, éclairage, flou, bruit, JPEG, 180-420 px) via `tools/benchmark_card_embeddings.py`.
  - `core/card_identifier.py` : embedders `dnn` (MobileNetV2 pool 1280-d via cv2.dnn) et `classic` (Lab+gradients pur OpenCV), `CardIndex` (build/save/load, recherche FAISS→numpy), `CardIdentifier.identify(crop)`.
  - `tools/build_card_index.py` (+ `--check`, `--download-model` avec troncature ONNX), `models/mobilenetv2_embeddings.onnx` committé (9 Mo).
  - Intégration détection (config `identify_cards`/`identify_min_score`, overlay nom exact + set + numéro, prix par card_id, CLI `--identify`) et GUI (case « 🎴 Identify Cards »).
  - 33 tests ; suite 205 passés / 0 échec ; ruff OK.
- **Décisions** :
  - MobileNetV2 via cv2.dnn plutôt que CLIP/torch : l'egress de l'environnement bloque api.tcgdex.net, download.pytorch.org et huggingface.co (constaté, non contourné) — et le CNN léger dépasse déjà largement les critères (98,4 % top-1). Le benchmark reste rejouable avec d'autres backends sur la machine utilisateur.
  - Références indexées en **moyenne de 3 vues** (native, 300 px, 300 px floutée) : +11 pts de top-1 mesurés — le multicrop requête (+0,3 pt pour 2× la latence) est abandonné.
  - Le modèle ONNX est **tronqué à la couche global-pool** et committé : cv2.dnn/OpenCV 5 ignore le nom de couche à `forward()`, impossible d'extraire les features du modèle complet (logits = 91 % seulement).
  - Une seule langue par carte dans l'index (artwork identique, dédoublonnage au build).
- **Prochaine étape** : F03 (mode « scan de collection », s'appuie sur F01).

### 2026-07-12 (session 6) — F07 implémentée, vague 2 complète
- **Features** : F07
- **Fait** :
  - `core/run_analyzer.py` : parsing runs Ultralytics, résumé au meilleur epoch, comparaison A/B, scoring des pires prédictions (IoU + appariement glouton), planche contact annotée, résolution de source (set réel F08 > val synthétique).
  - `gui/evaluation_view.py` : vue « 📊 Evaluation » (sidebar PROCESSING) — sélecteur de runs, artefacts, comparaison, pires prédictions en thread.
  - Monolithe : +15 lignes seulement (nav + dispatch + fallback d'erreur).
  - 19 tests ; suite 172 passés / 0 échec ; smoke test xvfb validé (capture).
- **Décisions** :
  - Pas de matplotlib embarqué : les PNGs d'Ultralytics sont réutilisés tels quels (zéro dépendance, zéro recalcul).
  - Le real_mAP (F08) est rattaché au run via le chemin absolu de son best.pt dans l'historique JSON.
  - Score « pire prédiction » = manqués + faux positifs + mauvaises classes (IoU ≥ 0.5, appariement glouton par IoU décroissante).
- **Prochaine étape** : vague 3 — F01 (identification fine par embeddings).

### 2026-07-12 (session 5) — F08 : infrastructure du set réel
- **Features** : F08 (80 %)
- **Fait** :
  - `datasets/real_val/` + README (protocole de capture reproductible).
  - `core/real_validation.py` : check du set, validation des labels YOLO, garde anti-fuite MD5, `evaluate_real_map()` (Ultralytics), rapport JSON avec historique, CLI `--check`.
  - Hook automatique en fin de `TrainingManager.train()` (non bloquant).
  - `tools/preannotate_real_val.py` : pré-annotation par le modèle courant.
  - 20 tests ; suite 153 passés / 0 échec.
- **Décisions** :
  - Garde anti-fuite par hash MD5 (copie exacte) — suffisant pour la règle « jamais dans le train » ; la détection de quasi-doublons (recadrages) est hors périmètre.
  - Le data.yaml d'évaluation est généré depuis les classes du MODÈLE (pas du dataset) : on peut évaluer n'importe quel .pt.
  - `real_mAP` historisé en JSON pour mesurer l'impact des vagues de génération (F04/F05).
- **Bloqué par l'utilisateur** : photos réelles à déposer (cf. point de reprise).
- **Prochaine étape** : F07 (onglet Évaluation, qui affichera aussi real_mAP).

### 2026-07-12 (session 4) — F06 implémentée, vague 1 complète
- **Features** : F06
- **Fait** :
  - Refactor `core/augmentation_albumentations.py` : pool paramétrable (`build_transform_pool`) + `preview_augmentations` (direct, reproductible par seed, compatible albumentations 1.x/2.x).
  - `gui/augmentation_preview.py` : fenêtre Live Preview (sliders, catégories, grille 1+6, debounce, thread + queue pollée), bouton « 👁 Live Preview » dans la vue Augmentation.
  - 17 tests + smoke test xvfb (capture d'écran validée) ; suite 133 passés / 0 échec.
- **Décisions** :
  - Aperçus rendus via `tk.PhotoImage(data=base64 PNG)` : pas de dépendance Pillow ajoutée.
  - Module import-safe sans tkinter (stub) pour les environnements headless.
  - Le pipeline de production reste inchangé (intensity=1.0) tant que la génération n'accepte pas ces paramètres (backlog noté dans la fiche F06).
- **Prochaine étape** : vague 2 — F08 (infrastructure du set de validation réel).

### 2026-07-12 (session 3) — F05 implémentée
- **Features** : F05
- **Fait** :
  - `core/occlusion_effects.py` : sleeve, éventail (fan_layout), doigts procéduraux, calcul de fraction visible, découpe en éventails.
  - `core/mosaic_optimized.py` : layout_mode 4 (`_compose_fan_group`) — ombres inter-cartes, sleeves 50 %, doigts 50 % des éventails, filtre d'annotation < 25 % visible, bboxes clippées.
  - GUI : « 4 - Fan / Hand (Occlusions) » ; CHANGELOG et FEATURES.md à jour.
  - 15 tests ; suite complète 111 passés / 0 échec ; démo visuelle validée (bboxes tracées).
- **Décisions** :
  - Annotation **amodale** (étendue complète de la carte, clippée au canvas) : convention standard YOLO sous occlusion.
  - Seuil de visibilité 25 % (`MIN_VISIBLE_FRACTION`) pour exclure les cartes quasi masquées des labels.
  - Doigts procéduraux plutôt qu'assets PNG (cohérence avec F04 : zéro asset externe).
- **Prochaine étape** : F06 (prévisualisation live des augmentations).

### 2026-07-12 (session 2) — F04 implémentée
- **Features** : F04
- **Fait** :
  - `core/background_generator.py` : générateur procédural (5 catégories), `add_drop_shadow`, `apply_camera_effects`.
  - `core/mosaic_optimized.py` : background_mode 3 (fond réaliste + ombres portées + effets caméra).
  - GUI : nouvelle valeur « 3 - Realistic (Procedural) » dans Settings → Mosaic.
  - `tools/generate_realistic_backgrounds.py` : pré-génération + galerie de contrôle (`--gallery`).
  - 17 tests (`tests/test_background_generator.py`) ; suite complète 96 passés / 0 échec.
  - Docs : FEATURES.md, CHANGELOG `[Unreleased]`.
- **Décisions** :
  - Génération **procédurale** plutôt que téléchargement de textures (licences, hors-ligne, variété infinie, seed).
  - La perspective n'est pas re-implémentée : `transform_mode 1` (rotation 3D) la couvre déjà.
  - Les effets caméra sont appliqués sur l'image composée finale, uniquement en mode 3.
  - Catégorie « mains » reportée sur F05 (overlays de doigts, même mécanique d'occlusion).
- **Prochaine étape** : F05 (occlusions réalistes).

### 2026-07-12 — Initialisation
- **Features** : toutes (F01–F10)
- **Fait** :
  - Proposition des 10 features, toutes validées par l'utilisateur.
  - Création de ce journal de suivi (`docs/JOURNAL_FEATURES.md`).
  - Définition de l'ordre de réalisation en 4 vagues (qualité modèle → mesure → valeur produit → confort).
- **Décisions** :
  - Branche de travail : `claude/new-feature-proposals-v4x2m3`.
  - Commits préfixés par l'ID de feature (`feat(F04): ...`).
  - F08 (set réel) placé avant F07 dans la vague 2 pour pouvoir mesurer l'impact de la vague 1 au plus tôt.
- **Prochaine étape** : design de F04 (cf. Point de reprise).
