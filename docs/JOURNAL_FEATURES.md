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
| F01 | Identification fine de la carte (embeddings + FAISS) | Détection | ⭐ Haute | ⬜ | 0 % |
| F02 | Estimation de l'état de la carte (grading) | Détection | Basse | ⬜ | 0 % |
| F03 | Mode « scan de collection » (inventaire + valeur) | Détection | ⭐ Haute | ⬜ | 0 % |
| F04 | Backgrounds réalistes automatiques | Dataset | ⭐ Haute | 🟡 | 90 % |
| F05 | Occlusions réalistes (éventails, sleeves, mains) | Dataset | Moyenne | 🟢 | 100 % |
| F06 | Prévisualisation live des augmentations (GUI) | Dataset | Moyenne | ⬜ | 0 % |
| F07 | Onglet « Évaluation » (PR, confusion, pires prédictions) | Training | Moyenne | ⬜ | 0 % |
| F08 | Set de validation « réel » annoté + métrique dédiée | Training | Moyenne | ⬜ | 0 % |
| F09 | Historique et alertes de prix (SQLite + sparklines) | Prix | Basse | ⬜ | 0 % |
| F10 | Cache API hors-ligne (snapshot des prix) | Prix | Basse | ⬜ | 0 % |

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

- **Dernière session** : 2026-07-12 (session 3)
- **Feature en cours** : F05 terminée (100 %). F04 à 90 % (validation quantitative sur photos réelles en attente de F08).
- **Prochaine étape concrète** : démarrer **F06 (Prévisualisation live des augmentations)** — d'abord exposer une fonction `preview(image, params)` dans `core/augmentation_albumentations.py` (sans sous-processus), puis nouvelle vue GUI avec sliders + grille d'aperçus + debounce. Vague 1 complète après F06.
- **En attente de décision utilisateur** : rien
- **Pièges / notes connues** :
  - `core/mosaic_optimized.py` : `_process_single_group` tourne dans des sous-processus (`ProcessPoolExecutor`) — tout nouvel état doit être picklable et passé via le tuple `args`.
  - Le combobox « Background Mode » de la GUI (`gui/settings_dialog.py`) stocke des chaînes `"3 - Realistic (Procedural)"` dans un `IntVar` — comportement hérité, ne pas « corriger » isolément.
  - Les effets caméra sont appliqués UNIQUEMENT en mode 3, après compositing (sinon double vignettage si on les mettait aussi dans le fond).

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

- [ ] Design : choix du modèle d'embedding (CLIP vs CNN léger), benchmark rapide sur 50 cartes
- [ ] Script de construction de l'index FAISS depuis `images/`
- [ ] `core/card_identifier.py` : API `identify(crop) -> (card_id, score, top_k)`
- [ ] Intégration dans `DetectionManager` (option activable, seuil de confiance)
- [ ] Affichage GUI : nom exact + set + numéro dans l'overlay de détection
- [ ] Tests : précision top-1/top-5 sur un échantillon, tests unitaires de l'index
- [ ] Docs : section dans `docs/FEATURES.md` + entrée CHANGELOG

**Critères d'acceptation** : top-1 ≥ 90 % sur cartes bien cadrées ; latence < 50 ms par carte sur CPU ; fonctionne sur un set jamais vu par YOLO.

**Notes de session** : —

---

### F02 — Estimation de l'état de la carte (grading)

**Objectif** : estimer l'état (centrage, coins, rayures de surface) depuis la webcam et pondérer le prix affiché (Near Mint vs Played).

**Fichiers/Modules concernés** : `core/detection_manager.py`, nouveau `core/card_grader.py`

- [ ] Design : quelles métriques sont réalistes avec une webcam (centrage = faisable ; rayures = difficile, à valider)
- [ ] Détection du centrage (bords intérieurs/extérieurs, ratio)
- [ ] Détection de coins abîmés (heuristique contours ou petit classifieur)
- [ ] Pondération du prix selon l'état estimé
- [ ] Affichage GUI (badge d'état sur l'overlay)
- [ ] Tests + docs

**Critères d'acceptation** : centrage mesuré à ±5 % vs mesure manuelle ; l'estimation ne bloque jamais la détection (best effort).

**Notes de session** : —

---

### F03 — Mode « scan de collection »

**Objectif** : session de détection continue qui déduplique les cartes vues, construit un inventaire
(CSV/Excel — réutiliser `excel/`) avec valeur totale de la collection en fin de session.

**Dépend de** : F01 (identification exacte) fortement recommandé ; possible en mode dégradé (classes YOLO seules) avant.

**Fichiers/Modules concernés** : `core/detection_manager.py`, `excel/`, nouveau `core/collection_scanner.py`, GUI (nouvelle vue ou mode dans la vue Détection)

- [ ] Design : logique de déduplication (tracking + identification stable sur N frames)
- [ ] `core/collection_scanner.py` : accumulation, dédup, agrégats (nb cartes, valeur totale)
- [ ] Récupération des prix par carte (réutiliser l'intégration Cardmarket/TCGPlayer existante)
- [ ] Export CSV + Excel de l'inventaire
- [ ] GUI : bouton « Démarrer un scan », compteur live, écran récap de fin de session
- [ ] Tests + docs

**Critères d'acceptation** : une même carte présentée 10 s n'apparaît qu'une fois ; export Excel ouvrable avec totaux corrects.

**Notes de session** : —

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

- [ ] Design : quels paramètres exposer en sliders ; échantillonnage (1 carte, N variantes)
- [ ] Refactor léger : exposer une fonction `preview(image, params) -> image` dans le module d'augmentation
- [ ] Vue GUI : choix de la carte, grille de N aperçus, bouton « regénérer », debounce sur les sliders
- [ ] Application des paramètres validés vers la config de génération
- [ ] Tests (la preview n'altère pas la config globale) + docs

**Critères d'acceptation** : rafraîchissement < 500 ms pour 6 aperçus ; aucun sous-processus lancé ; paramètres reportables en un clic dans la config.

**Notes de session** : —

---

### F07 — Onglet « Évaluation »

**Objectif** : courbes PR, matrice de confusion, galerie des pires prédictions dans la GUI,
avec comparaison entre deux runs d'entraînement.

**Fichiers/Modules concernés** : `core/training_manager.py`, `gui/` (nouvelle vue), sorties Ultralytics dans `output/`/`runs/`

- [ ] Design : réutiliser les artefacts Ultralytics (results.csv, confusion_matrix.png) vs recalcul custom
- [ ] Parsing des runs disponibles + sélection dans la GUI
- [ ] Affichage courbes PR / F1 / loss (matplotlib embarqué dans Tkinter)
- [ ] Galerie « pires prédictions » (images val triées par erreur)
- [ ] Comparaison côte à côte de deux runs
- [ ] Tests + docs

**Critères d'acceptation** : tout run existant est visualisable sans relancer d'entraînement ; comparaison A/B lisible.

**Notes de session** : —

---

### F08 — Set de validation « réel » annoté

**Objectif** : un mini-set de photos de vraies cartes, annoté, séparé du dataset synthétique,
avec une métrique dédiée pour mesurer le vrai transfert au monde réel.

**Fichiers/Modules concernés** : `core/training_manager.py`, `core/dataset_validator.py`, nouveau dossier `datasets/real_val/` (ou équivalent)

- [ ] Design : protocole de capture (nb de photos, conditions d'éclairage, appareils)
- [ ] Structure du set réel + convention d'annotation (format YOLO)
- [ ] Outil d'annotation assisté (pré-annotation avec le modèle courant + correction manuelle) — optionnel
- [ ] Script d'évaluation `real_mAP` séparé de la val synthétique
- [ ] Intégration au rapport de fin d'entraînement + onglet Évaluation (F07)
- [ ] Docs (protocole de capture reproductible)

**Critères d'acceptation** : `real_mAP` calculé et affiché après chaque entraînement ; le set réel n'entre JAMAIS dans le train.

**Notes de session** : —

---

### F09 — Historique et alertes de prix

**Objectif** : stocker les prix relevés en SQLite, afficher des sparklines d'évolution,
notifier quand une carte de l'inventaire dépasse un seuil.

**Dépend de** : F10 (même couche de persistance des prix) ; F03 pour la notion d'inventaire.

**Fichiers/Modules concernés** : nouveau `core/price_store.py`, `core/detection_manager.py`, GUI

- [ ] Design : schéma SQLite (carte, source, prix, devise, timestamp), fréquence de relevé
- [ ] `core/price_store.py` : écriture à chaque relevé, requêtes d'historique
- [ ] Sparklines dans la GUI (inventaire et/ou overlay)
- [ ] Alertes de seuil (notification GUI ; extension possible : mail/webhook)
- [ ] Tests + docs

**Critères d'acceptation** : historique persistant entre sessions ; alerte déclenchée de façon fiable au franchissement de seuil.

**Notes de session** : —

---

### F10 — Cache API hors-ligne

**Objectif** : snapshot local des prix pour utiliser la détection sans réseau.

**Fichiers/Modules concernés** : `core/tcgdex_api.py`, intégrations prix existantes, nouveau cache (fichier ou SQLite partagé avec F09)

- [ ] Design : stratégie de cache (TTL, invalidation, taille), format (SQLite recommandé pour préparer F09)
- [ ] Couche cache transparente devant les appels API prix
- [ ] Commande/bouton « Précharger les prix » pour un set ou l'inventaire
- [ ] Mode hors-ligne explicite (indicateur GUI « prix du JJ/MM »)
- [ ] Tests (hit/miss/expiration, mode avion) + docs

**Critères d'acceptation** : détection + affichage prix 100 % fonctionnels sans réseau après préchargement ; date du snapshot visible.

**Notes de session** : —

---

## 📆 Journal de bord

> Entrées antéchronologiques (la plus récente en haut).
> Format : date, auteur/session, features touchées, ce qui a été fait, décisions prises.

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
