# 🐛 Recherche approfondie de bugs — Juillet 2026

Audit complet du code (`core/`, `scripts/`, `gui/`, `gui_qt/`, GUI Tkinter),
par lecture ligne à ligne des 25 modules du core et des points d'orchestration.
Les findings sont classés par gravité. Chaque entrée référence les fichiers et
lignes concernés (état du dépôt au commit `c30aa8e`).

> Aucun correctif n'est appliqué dans ce commit : ce document est le livrable
> de la phase de recherche. Chaque bug est indépendant et peut être corrigé
> séparément.

---

## 🔴 Critiques (corruption de données / fonctionnalité cassée)

### C1. Le téléchargement d'un set ÉCRASE toute la base de cartes
`core/manifest_tools.py:19-92`, `core/image_downloader.py:311-319`,
`gui_qt/views/download.py:116-124`, `GUI_v3.1_modern.py:4577-4586`

`generate_yaml_from_manifest()` **réécrit intégralement** `models/cards_database.yaml`
à partir du seul `manifest.csv` du dernier téléchargement — et `download_set()`
écrase `images/manifest.csv` à chaque set (il n'y écrit que les cartes du set
courant). Conséquence : télécharger un 2ᵉ set **supprime le 1ᵉʳ de la base** :

- les `class_id` (dérivés de l'ordre du YAML par `load_card_data()`) changent,
  invalidant tous les labels déjà générés ;
- les prix et métadonnées déjà renseignés sont perdus (tout repart à
  `price: None`).

Correctif suggéré : fusionner avec le YAML existant (mise à jour/ajout par
`card_id`) au lieu de réécrire, ou générer un manifest par set.

### C2. Workflow automatique : l'étape mosaïques est un no-op silencieux
`core/workflow_manager.py:276-283` vs `core/mosaic_optimized.py:720-723`

Pour les modes `quick`, `standard` et `complete`, le WorkflowManager lance
`core/mosaic_optimized.py all`. Or le `main()` de ce module répond
`"⚠️ Mode ALL non encore optimisé"` puis `return` avec le code 0. L'étape est
donc marquée **SUCCESS avec 0 mosaïque générée**, et le dataset final ne
contient que les cartes isolées augmentées.

### C3. Workflow mode `custom` : le nombre de mosaïques passé comme layout_mode
`core/workflow_manager.py:280`

```python
cmd = [sys.executable, "core/mosaic_optimized.py", str(self.config.mosaic_count), "0", "0"]
```

`mosaic_count` (ex. 500) est envoyé en 1ᵉʳ argument positionnel =
`layout_mode`. Un layout 500 tombe dans la branche `else` (grille), et aucun
`--max-groups` n'est passé : le nombre demandé est ignoré.

### C4. Auto-balancer : bounding boxes faussées par le scale
`core/auto_balancer_optimized.py:189-205, 266-275`

Le pipeline d'augmentation inclut `iaa.Affine(scale=(0.9, 1.1))` mais
`_adjust_yolo_bbox_for_augmentation()` ne corrige que le flip horizontal. Le
commentaire *« Le scale imgaug n'affecte pas les coordonnées normalisées
YOLO »* est faux : un zoom autour du centre déplace les bords de l'objet
(`w' = w×s`, `cx' = 0.5 + (cx−0.5)×s`). Toutes les images `_balN` générées
avec scale ≠ 1 ont des bboxes décalées jusqu'à ~10 %.

### C5. Le balancing après merge n'est jamais vu par l'entraînement
`scripts/merge_dataset.py:179-185`, `core/workflow_manager.py:415-430`,
`gui_qt/views/tools.py:61-77`, `GUI_v3.1_modern.py:5745-5747`

Le `data.yaml` du dataset final pointe `train.txt` / `val.txt` (listes de
chemins absolus figées au merge). L'auto-balancer, lancé APRÈS le merge sur
`output/dataset`, ajoute des images `_balN` (jamais listées → **ignorées à
l'entraînement**) et, en stratégie `reduce`, supprime des fichiers **toujours
listés** dans train.txt → erreurs/​warnings Ultralytics sur images manquantes.
Il faut régénérer train.txt/val.txt (ou pointer sur les dossiers) après le
balancing.

### C6. tcgdex_api : mapping des sets décalé → prix de la MAUVAISE carte
`core/tcgdex_api.py:43-60` vs `core/image_downloader.py:25-45` (correct)

```python
'shrouded fable': 'sv06',       # réel : sv06.5
'twilight masquerade': 'sv05',  # réel : sv06
'temporal forces': 'sv04',      # réel : sv05
'paldean fates': 'sv03',        # réel : sv04.5
'paradox rift': 'sv02',         # réel : sv04
'obsidian flames': 'sv01',      # réel : sv03
```

La stratégie 1 de `search_card_with_prices()` construit un ID du type
`sv02-001` pour « Paradox Rift 001 »… qui existe (Paldea Evolved 001) : l'API
répond 200 et renvoie **le prix d'une autre carte**, sans erreur détectable.
`POPULAR_SETS` d'image_downloader contient les bons codes — réutiliser cette
source unique.

### C7. Stratégies de balancing du workflow non supportées par le balancer
`core/workflow_manager.py:71` (`"augment", "undersample", "remove"`) vs
`core/auto_balancer_optimized.py:340` (`choices=['augment', 'reduce', 'both']`)

Toute configuration autre que `augment` fait échouer l'étape sur une erreur
argparse (non bloquante, mais le balancing n'a pas lieu).

---

## 🟠 Élevés

### E1. workflow_optimized.py : l'étape merge échoue toujours
`scripts/workflow_optimized.py:118`

`run_command(f'{python_exe} merge_dataset.py')` est exécuté depuis la racine
du projet, mais le script vit dans `scripts/` → « can't open file ». De plus,
l'étape 1 génère des images holographiques dans `output/holographic` que le
reste du pipeline **n'utilise jamais** (l'étape 2 repart de `images/`), et
`total_images = 8` est codé en dur pour les estimations.

### E2. Auto-balancer : comptage par occurrences, pas par images
`core/auto_balancer_optimized.py:74-99, 310-330`

`analyze()` ajoute le nom d'image **une fois par occurrence** de la classe
(une mosaïque avec 3 cartes de la classe X compte 3 fois). Conséquences :
cibles faussées ; `_reduce_class` fait `random.sample()` sur une liste avec
doublons (peut tirer 2× le même fichier) et supprime des images qui
contiennent **d'autres classes**, déséquilibrant le reste du dataset.

### E3. Mosaïques : bboxes non clippées au canvas (layouts 1-3)
`core/mosaic_optimized.py:602-614`

`min_x/max_x/min_y/max_y` ne sont pas bornés à `[0, canvas]`. En
transformation 3D (`transform_mode=1`, surtout layout 2 avec θ ∈ ±180°), la
projection perspective peut agrandir la carte au-delà de sa cellule → des
coordonnées YOLO **hors [0,1]** sont écrites. `dataset_validator` les classe
ensuite en « erreurs critiques » (`annotations_out_of_bounds`) : le pipeline
se signale lui-même en erreur. Le layout 4, lui, clippe correctement
(`mosaic_optimized.py:465-468`) — faire pareil dans le chemin standard.

### E4. device="0" par défaut → plantage sur machine sans GPU CUDA
`core/detection_manager.py:40`, `core/training_manager.py:49`

Ultralytics lève « Invalid CUDA device » si CUDA est absent. Défaut plus sûr :
auto-détection (`"0" if torch.cuda.is_available() else "cpu"`).

### E5. Fallback de load_paths() incomplet → KeyError à l'import
`core/utils.py:54-67` vs `core/mosaic_optimized.py:72-77`,
`core/augmentation_albumentations.py:63-66`

Si `config/paths.json` est absent, le dict de secours ne contient ni
`output_augmented_images`, ni `output_backgrounds`, ni `output_mosaics_*` :
l'import de `mosaic_optimized` / `augmentation_albumentations` plante en
KeyError au lieu du fonctionnement dégradé voulu.

---

## 🟡 Moyens

### M1. merge_dataset : division par zéro et images sans label
`scripts/merge_dataset.py:36-47, 186-188, 205-217`

- `len(train_files)/total*100` → **ZeroDivisionError** si les dossiers source
  sont vides ;
- `copy_files()` copie l'image même sans label (compteur faussé, images
  « background » silencieuses dans le dataset) ;
- si `augmented/data.yaml` existe mais sans clé `names`, `class_names={}` →
  `data.yaml` final avec `nc: 1` et `names: ["unused"]`.

### M2. Split train/val avec fuite de données
`scripts/merge_dataset.py:51-73`

Le split aléatoire ne sépare pas les variantes : les 30 augmentations d'une
même carte se retrouvent en train ET en val → métriques de validation
optimistes. Idéalement, splitter par carte source (et garder la val
synthétique distincte du set réel F08, déjà géré).

### M3. Effet holographique : couleurs RGB sur images BGR + gradient dégénéré
`core/holographic_augmenter_optimized.py:53-61, 77-101`

- `rainbow_colors` est déclaré en RGB mais appliqué via `cv2.addWeighted` sur
  des images BGR : violet/rouge inversés avec le bleu (cosmétique) ;
- le dénominateur `width·cos(θ) + height·sin(θ)` s'annule ou devient négatif
  pour θ > 90° (l'angle est tiré dans [0, 180]) : gradient dégénéré sur ~la
  moitié des tirages (pas de crash, mais rendu incohérent).

### M4. tcgdex search_cards télécharge le catalogue complet
`core/tcgdex_api.py:62-93`

`GET /{lang}/cards` renvoie l'intégralité des cartes (dizaines de milliers)
avec `timeout=15` : lent et fragile. Utiliser le filtre serveur
(`/cards?name=...`) comme le fait déjà `resolve_set()` pour les sets.

### M5. Prix à 0 traités comme absents
`core/tcgdex_api.py:145-181`

`if cm_price:` / `if price:` écartent un prix de `0.0` (falsy) — utiliser
`is not None`.

### M6. workflow_manager._run_subprocess sans encodage explicite
`core/workflow_manager.py:509-537`

`text=True` sans `encoding='utf-8', errors='replace'` → UnicodeDecodeError
possible sous Windows (cp1252) car tous les sous-processus émettent des
emojis. `gui/task_runner.py:124-133` fait la bonne chose ; harmoniser.

### M7. dataset_exporter : data.yaml Roboflow incohérent, API ambiguë
`core/dataset_exporter.py:24-36, 284-292`

- `names: list(class_names.values())` n'est pas aligné sur les IDs si les
  classes ne sont pas contiguës ; sans `class_names`, `nc: 1` quelle que soit
  la réalité du dataset ;
- la docstring annonce une « Liste des noms de classes » mais le code exige un
  dict (`.get(class_id)`), sinon AttributeError.

### M8. Mosaïques : dossiers `corrupted/` et `web/` relatifs au CWD
`core/mosaic_optimized.py:128-141, 308-317`

Créés là où le processus est lancé (pollution hors projet si CWD ≠ racine) ;
le déplacement vers `corrupted/` se fait depuis des threads pendant que
d'autres lisent le même dossier. Fonds web jamais nettoyés ni réutilisés
(retéléchargés par chaque worker).

### M9. Auto-balancer : préchargement RAM inutile
`core/auto_balancer_optimized.py:276-296` vs `211-215`

`source_images` charge toutes les images de la classe en mémoire… puis
`_augment_single_image` **relit chaque image depuis le disque**. Le cache ne
sert qu'à vérifier l'extension : coût mémoire pur.

### M10. CollectionScanner : tracks jamais expirés
`core/collection_scanner.py:130, 188-201`

Un faux positif fugace crée un `_Track` qui persiste toute la session ; deux
autres faux positifs de la même classe, même à 20 minutes d'écart, suffisent
à le « confirmer » dans l'inventaire. Ajouter une expiration (dernier hit trop
ancien → reset).

### M11. GUI : layout 4 (éventails F05) et background 3 (réaliste F04)
inaccessibles
`gui_qt/views/mosaic.py:8-12`, GUI Tkinter (combos équivalents)

Les deux interfaces ne proposent que layouts 1-3 et backgrounds 0-2 alors que
le core supporte layout 4 et background 3 — les deux features phares F04/F05
ne sont atteignables qu'en CLI.

---

## 🔵 Mineurs

- `core/utils.py:333-334` — le fallback de `extract_card_number` valide
  `re.match(r'\d{3}', ...)` sans ancrage de fin : « 1234 » passe.
- `core/utils.py:236-250` — collision des clés courtes de `load_card_data` :
  deux sets contenant le numéro « 019 » → la clé courte pointe le premier set
  chargé (comportement à documenter ; les clés complètes sont sûres).
- `core/augmentation_albumentations.py:439` — labels toujours
  `0.5 0.5 1.0 1.0` ; correct pour une carte plein cadre, légèrement trop
  large après `SafeRotate`/`Perspective` (la carte n'occupe plus tout le
  cadre).
- `core/mosaic_optimized.py:716-718` — sans fonds « fake », les vraies cartes
  servent de fond **sans annotation** : le modèle apprend à ignorer des cartes
  réelles.
- `core/detection_manager.py:479` — `cv2.imread()` non vérifié avant
  `_annotate_frame` (crash si l'image devient illisible entre détection et
  annotation).
- `core/auto_balancer_optimized.py:85-92` — l'affichage de la distribution
  duplique des classes quand il y en a ≤ 20 (tranches `[:10]` et `[-10:]` qui
  se recouvrent).
- `core/price_cache.py:230-238` — `latest_all()` repose sur le comportement
  SQLite « bare columns with MAX() » ; correct en SQLite mais fragile si la
  requête est portée ailleurs.
- `scripts/merge_dataset.py:36` — seuls les `*.png` sont fusionnés ; des
  sources `.jpg` seraient silencieusement ignorées.
- `core/random_erasing.py:44-59` — boucle de rejet potentiellement longue
  quand le rectangle tiré dépasse l'image (pas de borne d'essais).

---

## ✅ Points vérifiés sans problème notable

- `core/occlusion_effects.py`, `core/background_generator.py` (F04/F05) —
  clipping, masques et fractions de visibilité corrects.
- `core/card_identifier.py` (F01), `core/card_grader.py` (F02),
  `core/real_validation.py` (F08, garde anti-fuite MD5 solide),
  `core/run_analyzer.py` (F07), `core/price_cache.py` (F10, schéma et alertes
  F09 cohérents), `gui/task_runner.py` / `gui_qt/bridge.py` (threading propre).
- Compilation de tout le dépôt (`compileall`) : aucune erreur de syntaxe.

---

## 🎯 Ordre de correction recommandé

1. **C1** (perte de la base multi-sets) — le plus destructeur pour les données.
2. **C2/C3** (workflow mosaïques) — le pipeline « automatique » ne produit pas
   ce qu'il annonce.
3. **C4/E2/C5** (balancer : bboxes, comptage, train.txt) — qualité du dataset.
4. **C6** (mapping des sets) — prix silencieusement faux.
5. **E3, E4, E5** puis les moyens/mineurs.
