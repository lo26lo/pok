# 🌍 Set de validation RÉEL (F08)

Ce dossier contient des **photos de vraies cartes**, annotées à la main,
pour mesurer le transfert du modèle (entraîné sur données synthétiques)
vers le monde réel. La métrique produite est `real_mAP`, séparée de la
validation synthétique.

## ⚠️ Règle absolue

**Aucune image de ce dossier ne doit JAMAIS servir à l'entraînement.**
Une garde anti-fuite (hash MD5 contre les dossiers d'entraînement) refuse
l'évaluation si une image est retrouvée dans le train.

## Structure

```
datasets/real_val/
├── images/    photo_001.jpg, photo_002.jpg, ...
└── labels/    photo_001.txt, photo_002.txt, ...   (format YOLO)
```

Format YOLO d'une ligne de label : `class_id cx cy w h` (normalisés 0-1).
Les `class_id` doivent correspondre aux classes du modèle entraîné
(mêmes IDs que `output/dataset/data.yaml`). Un fichier vide = photo sans
carte (négatif), c'est utile aussi.

## 📸 Protocole de capture (reproductible)

Objectif : 30 à 100 photos couvrant la variété du monde réel.

1. **Appareils** : au moins 2 différents (smartphone + webcam utilisée en
   détection live) — c'est la webcam qui compte le plus.
2. **Éclairages** (varier, ~1/3 chacun) :
   - lumière du jour indirecte,
   - lampe intérieure chaude (soirée),
   - éclairage difficile : contre-jour léger, reflets sur sleeves.
3. **Surfaces** : tapis de jeu, table en bois, classeur, tissu — les mêmes
   familles que les fonds synthétiques (F04), plus au moins une surface
   non couverte par la génération.
4. **Dispositions** :
   - cartes seules à plat (~30 %),
   - plusieurs cartes espacées (~20 %),
   - cartes en éventail / tenues en main (~30 %, cf. F05),
   - sous sleeve ou toploader (~20 %).
5. **Angles** : de face, ~30°, ~45° ; quelques photos avec flou de bougé
   léger (réaliste webcam).
6. **Résolution** : native de l'appareil, pas de recadrage serré — la
   carte doit occuper entre 5 % et 60 % de l'image.

## 🏷️ Annotation

1. Déposer les photos dans `images/`.
2. Pré-annoter avec le modèle courant :
   ```bash
   python tools/preannotate_real_val.py
   ```
3. **Corriger à la main** chaque `.txt` généré (les prédictions du modèle
   ne sont qu'un brouillon) — n'importe quel outil YOLO fait l'affaire
   (labelImg, CVAT, ou édition directe).
4. Vérifier l'état du set :
   ```bash
   python core/real_validation.py --check
   ```

## 📊 Évaluation

- Automatique en fin d'entraînement (TrainingManager) si le set est prêt.
- Manuelle :
  ```bash
  python core/real_validation.py --model runs/train/pokemon_detector/weights/best.pt
  ```
- Rapport avec historique : `output/real_val_report.json` — permet de
  comparer le `real_mAP` avant/après chaque changement de génération
  (F04/F05 notamment).
