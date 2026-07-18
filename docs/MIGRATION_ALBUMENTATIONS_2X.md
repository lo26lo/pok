# 🔄 Migration albumentations 1.x → 2.x — Plan d'exécution

**Branche** : `claude/bug-research-deep-dive-z0zhgj` (suite de la PR #7)
**Statut global** : 🟡 EN COURS — les cases ci-dessous sont cochées au fil des
commits ; en cas d'interruption, reprendre à la première case non cochée.

## Contexte (résumé de l'analyse préalable)

- Toute l'API albumentations est concentrée dans
  `core/augmentation_albumentations.py` (pool de 25 transforms, `SomeOf`,
  `Compose(seed=)`).
- Sous 2.0.8, **tout s'exécute sans erreur ni warning visible**, mais
  4 transforms **ignorent silencieusement** leurs arguments 1.x et retombent
  sur les défauts 2.x (audit empirique attribut par attribut) :

  | Transform | Arg 1.x (ignoré en 2.x) | Remplacement 2.x |
  |---|---|---|
  | `GaussNoise` | `var_limit=(10, 40·i)` | `std_range=(√10/255, √(40·i)/255)` — conversion variance 0-255 → écart-type normalisé |
  | `ImageCompression` | `quality_lower=60, quality_upper=95` | `quality_range=(60, 95)` |
  | `RandomSunFlare` | `angle_lower/upper`, `num_flare_circles_lower/upper` | `angle_range=(0, 1)`, `num_flare_circles_range=(3, 6)` |
  | `RandomFog` | `fog_coef_lower/upper` | `fog_coef_range=(0.1, max(0.1, 0.3·i))` |

  Les 21 autres transforms passent inchangés (audit vérifié).
- Le chemin seed de la preview est déjà bi-mode (`Compose(seed=)` +
  fallback `TypeError`) et reproductible sous 2.x — rien à faire.
- **Bonus débloqué** : le transport de bboxes de `SafeRotate`, cassé en
  1.4.x (bbox 0.9×0.9 @10° → h=0.064), est réparé en 2.x (→ 0.902) ⇒ on
  peut passer les labels d'augmentation du plein cadre `0.5 0.5 1.0 1.0`
  à des bboxes réellement transformées (finding 📝 de l'audit).
- **Connexe** : `core/auto_balancer_optimized.py` importe encore `imgaug`
  à l'exécution, absent de `config/requirements.txt` (remplacé par
  albumentations) ⇒ la stratégie `augment` du balancer échoue en
  ImportError sur une installation propre. Le port fait partie de cette
  migration.

**Décisions prises** : coupure franche vers 2.x (pas de double-support,
un seul fichier concerné) ; le balancer utilise `bbox_params`
d'albumentations au lieu de la reconstruction par keypoints.

## Phases

### ✅ Phase 0 — Ce plan (commit d'ancrage)
- [x] `docs/MIGRATION_ALBUMENTATIONS_2X.md` rédigé, commité, poussé

### ✅ Phase 1 — Migration du pool de transforms
- [x] `config/requirements.txt` : `albumentations>=1.3.0,<2.0` → `>=2.0,<3`
- [x] `build_transform_pool()` : les 4 transforms du tableau ci-dessus
      passés aux arguments 2.x (avec conversion pour GaussNoise)
- [x] Vérifier les mentions de version dans `docs/INSTALLATION.md` et
      `config/requirements_extra.txt`
- [x] Env de dev : `pip install "albumentations>=2.0,<3"` puis suite verte

### ✅ Phase 2 — Test de régression des amplitudes
- [x] Nouveau test : instancier le pool (i=1.0) et vérifier les valeurs
      EFFECTIVES des attributs (`std_range`, `quality_range`,
      `num_flare_circles_range`, `fog_coef_range` + échantillon des 21
      autres) — c'est LA protection contre les défauts silencieux
- [x] Vérifier aussi la mise à l'échelle par `intensity` (i=2.0)

### ✅ Phase 3 — Labels bbox-aware (finding 📝 de l'audit)
- [x] `AugmentationAlbumentations` : envelopper chaque `SomeOf` de
      génération dans `A.Compose(..., bbox_params=BboxParams(format='yolo',
      label_fields=['class_labels'], clip=True))`
- [x] `augment_image()` accepte/retourne la bbox ; `augment_batch()` écrit
      la bbox transformée (fallback plein cadre si liste vide)
- [x] La preview (`preview_augmentations`) reste image-seule (inchangée)
- [x] Test : labels générés dans [0,1], ≤ plein cadre, class_id préservé
- [x] Passer le finding correspondant du rapport d'audit à ✅

### ⬜ Phase 4 — Port du balancer imgaug → albumentations
- [ ] Remplacer le pipeline `iaa.Sequential` par l'équivalent albumentations :
      `Sometimes(0.5, Fliplr)` → `HorizontalFlip(p=0.5)` ;
      `Multiply(0.8-1.2)@0.3` → `RandomBrightnessContrast(brightness_limit=0.2,
      contrast_limit=0, p=0.3)` ; `GaussianBlur(sigma 0-1)@0.3` →
      `GaussianBlur(p=0.3)` ; `AdditiveGaussianNoise(0-0.05·255)@0.2` →
      `GaussNoise(std_range=(0, 0.05), p=0.2)` ; `Affine(scale 0.9-1.1)@0.2`
      → `Affine(scale=(0.9, 1.1), p=0.2)` ; `GammaContrast(0.8-1.2)@0.2` →
      `RandomGamma(gamma_limit=(80, 120), p=0.2)`
- [ ] Bboxes via `bbox_params` (supprime la reconstruction par keypoints
      et `_adjust_yolo_bbox_for_augmentation`)
- [ ] Supprimer l'import `imgaug` ; le balancer dépend d'albumentations
      (déjà dans requirements)
- [ ] Nouveau test fonctionnel du balancer : dataset synthétique →
      stratégie augment → compte + labels valides
- [ ] Mettre à jour la note « balancer nécessite imgaug » où elle existe

### ⬜ Phase 5 — Clôture
- [ ] Suite complète verte sous albumentations 2.x
- [ ] `docs/CHANGELOG.md` + rapport d'audit mis à jour
- [ ] Ce plan : toutes les cases cochées, statut passé à ✅ TERMINÉ
- [ ] Push final

## Commandes de validation (à relancer en cas de reprise)

```bash
pip install "albumentations>=2.0,<3"
python -m pytest tests/ -q                      # suite complète
python -m pytest tests/test_augmentation_amplitudes.py -v   # anti-régression
```

**Statut final** : 🟡 EN COURS (mettre à jour à la clôture).
