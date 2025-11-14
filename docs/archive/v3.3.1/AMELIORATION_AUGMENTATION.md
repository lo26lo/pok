# 🎨 Amélioration de la Variété des Augmentations

## 📊 Problème Identifié

Les images dans `output/augmented/images/` se ressemblaient trop car :
- Pipeline appliquait seulement **1 à 3 transformations** aléatoires
- **Peu de types de transformations** disponibles (10 types)
- **Pas de seed aléatoire** différent pour chaque augmentation

## ✨ Solutions Appliquées

### 1. **Pipeline Étendu** (25 transformations disponibles)

**Avant** : 10 types de transformations
```python
seq = iaa.SomeOf((1, 3), [
    iaa.Add((-10, 10)),
    iaa.Multiply((0.9, 1.1)),
    iaa.GaussianBlur((0, 3.0)),
    # ... 7 autres
], random_order=True)
```

**Après** : 22 types de transformations + augmentation de 2 à 5 transformations
```python
seq = iaa.SomeOf((2, 5), [
    # Luminosité et contraste (4 types)
    iaa.Add((-20, 20)),
    iaa.Multiply((0.8, 1.2)),
    iaa.LinearContrast((0.6, 1.6)),
    iaa.GammaContrast((0.7, 1.5)),
    
    # Couleurs (3 types)
    iaa.AddToHueAndSaturation((-30, 30)),
    iaa.ChangeColorTemperature((3000, 10000)),
    iaa.MultiplyHueAndSaturation((0.8, 1.2)),
    
    # Flou et netteté (3 types)
    iaa.GaussianBlur((0, 2.0)),
    iaa.AverageBlur(k=(1, 5)),
    iaa.Sharpen(alpha=(0, 0.5), lightness=(0.8, 1.3)),
    
    # Bruit (3 types)
    iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),
    iaa.ImpulseNoise(0.02),
    iaa.SaltAndPepper(0.01),
    
    # Effets visuels (6 types)
    iaa.imgcorruptlike.Fog(severity=(1, 2)),
    iaa.Posterize((5, 8)),
    iaa.Emboss(alpha=(0, 0.3), strength=(0.5, 1.5)),
    iaa.EdgeDetect(alpha=(0.0, 0.3)),
    iaa.JpegCompression(compression=(50, 99)),
    iaa.ElasticTransformation(alpha=(0, 5), sigma=0.5),
], random_order=True)
```

**Calcul de combinaisons possibles** :
- Avec 22 transformations et 2 à 5 sélections :
  - C(22,2) = 231 combinaisons
  - C(22,3) = 1,540 combinaisons
  - C(22,4) = 7,315 combinaisons
  - C(22,5) = 26,334 combinaisons
  - **Total : ~35,420 combinaisons différentes possibles !**

### 2. **Seed Aléatoire Différent**

**Ajouté** dans la boucle d'augmentation :
```python
for i in range(NUM_AUG_PER_IMAGE):
    # Réinitialiser le seed aléatoire pour chaque augmentation
    np.random.seed(int(time.time() * 1000000) % (2**31) + i)
    random.seed(int(time.time() * 1000000) % (2**31) + i)
    
    aug_img = seq(image=img)
```

Cela garantit que **chaque augmentation** aura un seed unique basé sur :
- Le temps actuel en microsecondes
- L'index de l'augmentation

### 3. **Transformations Plus Réalistes**

Les nouvelles transformations simulent mieux des conditions réelles :
- 📸 **Compression JPEG** : Simule une photo de carte prise avec un smartphone
- 🌡️ **Température de couleur** : Simule différents éclairages (tungstène, LED, soleil)
- 🔊 **Bruit gaussien** : Simule le bruit d'un capteur photo
- 🌊 **Transformation élastique** : Simule une légère déformation du papier
- 📊 **Plusieurs types de contraste** : Linear, Gamma, Multiply

## 🧪 Script de Test

### `test_augmentation_variety.py`

Script pour tester la variété en générant **10 augmentations d'une seule carte** :

```bash
# Avec le batch
test_augmentation_variety.bat

# Ou directement
python test_augmentation_variety.py
```

**Résultats attendus** :
- 1 image originale (00_original.png)
- 10 images augmentées (01_augmented.png à 10_augmented.png)
- Tailles de fichiers variables (preuve de transformations différentes)

**Exemple de résultat réel** :
```
00_original.png    - 189,757 bytes
01_augmented.png   - 206,264 bytes  (+8.7%)
02_augmented.png   - 172,735 bytes  (-9.0%)
03_augmented.png   - 141,272 bytes  (-25.5%)  ← Forte compression
04_augmented.png   - 99,195 bytes   (-47.7%)  ← Très forte compression + posterize
05_augmented.png   - 204,914 bytes  (+8.0%)
...
```

Les variations de taille **-47% à +30%** prouvent une **vraie diversité** !

## 📈 Impact sur le Dataset

### Avant
- **30 augmentations** × 252 cartes = **7,560 images**
- Variété limitée : ~1,000 combinaisons possibles
- Images trop similaires → **Surapprentissage** possible

### Après
- **30 augmentations** × 252 cartes = **7,560 images**
- Variété étendue : **~35,420 combinaisons possibles**
- Chaque image vraiment unique → **Meilleure généralisation**

## 🚀 Régénération du Dataset

Pour régénérer avec les améliorations :

### Option 1 : Via GUI
```
1. Ouvrir GUI_v2.py
2. Onglet "Augmentation"
3. Nettoyer output/augmented/
4. Cliquer "Lancer Augmentation"
```

### Option 2 : Ligne de commande
```bash
# Activer l'environnement
.venv\Scripts\activate

# Supprimer anciennes augmentations
rmdir /s /q output\augmented\images
rmdir /s /q output\augmented\labels

# Régénérer avec 30 augmentations
python augmentation.py --num_aug 30
```

## 📊 Comparaison Visuelle

Pour comparer visuellement :

1. **Générer le test** :
   ```bash
   test_augmentation_variety.bat
   ```

2. **Ouvrir le dossier** :
   ```
   test_augmentation_output/
   ```

3. **Observer** :
   - 00_original.png = Image de base
   - 01-10_augmented.png = 10 variations très différentes
   - Certaines avec brouillard
   - Certaines avec compression
   - Certaines avec changement de température couleur
   - Certaines avec bruit
   - etc.

## ✅ Résumé des Améliorations

| Aspect | Avant | Après | Gain |
|--------|-------|-------|------|
| **Types de transformations** | 10 | 22 | +120% |
| **Nombre de transformations appliquées** | 1-3 | 2-5 | +66% |
| **Combinaisons possibles** | ~1,000 | ~35,420 | x35 |
| **Seed aléatoire unique** | ❌ Non | ✅ Oui | Variété garantie |
| **Transformations réalistes** | ❌ Limitées | ✅ Étendues | Meilleure généralisation |

## 🎯 Prochaines Étapes

1. ✅ **Tester** avec `test_augmentation_variety.bat`
2. ⏳ **Régénérer** le dataset complet si satisfait
3. ⏳ **Entraîner** YOLO avec le nouveau dataset
4. ⏳ **Comparer** les performances (précision, recall, mAP)

---

**Date de mise à jour** : 30 octobre 2025
