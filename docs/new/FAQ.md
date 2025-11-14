# ❓ FAQ - Questions Fréquemment Posées

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025

---

## 📋 Table des Matières

1. [Installation & Configuration](#installation--configuration)
2. [GPU & Performance](#gpu--performance)
3. [Dataset & Images](#dataset--images)
4. [Augmentation](#augmentation)
5. [Mosaïques](#mosaïques)
6. [Entraînement YOLO](#entraînement-yolo)
7. [Détection](#détection)
8. [Prix & TCGdex API](#prix--tcgdex-api)
9. [Erreurs Courantes](#erreurs-courantes)
10. [Workflow](#workflow)

---

## 🔧 Installation & Configuration

### Q1: Quelle version de Python est recommandée ?

**A:** Python **3.12** (recommandé) ou **3.10/3.11** (supportés).

⚠️ **Python 3.13+ INTERDIT** : NumPy 2.0+ cause incompatibilité avec imgaug.

**Vérifier version** :
```batch
python --version
```

**Si Python 3.13+** :
- Désinstaller Python 3.13
- Installer Python 3.12 depuis [python.org](https://www.python.org/downloads/)
- Relancer `INSTALL.bat`

---

### Q2: L'installation échoue avec "NumPy 2.0 incompatible"

**A:** **NumPy 2.0+** n'est pas compatible avec **imgaug 0.4.0**.

**Solution** :
```batch
# Désinstaller NumPy 2.0+
pip uninstall numpy

# Installer NumPy 1.x (fixé)
pip install "numpy<2.0"

# Réinstaller dépendances
pip install -r config/requirements.txt
```

**Dans requirements.txt** :
```
numpy<2.0
```

---

### Q3: Comment activer le venv manuellement ?

**A:** 
```batch
# Windows
call .venv\Scripts\activate.bat

# Vérifier activation
python -c "import sys; print(sys.prefix)"
# Doit afficher: C:\DATA\pok\.venv
```

**Linux/Mac** :
```bash
source .venv/bin/activate
```

---

### Q4: `INSTALL.bat` ne fonctionne pas

**A:** **Causes possibles** :

1. **Python non ajouté au PATH**
   - Réinstaller Python avec "Add to PATH" coché
   
2. **Permission refusée**
   - Lancer `INSTALL.bat` en tant qu'Administrateur
   
3. **venv corrompu**
   ```batch
   rmdir /s /q .venv
   INSTALL.bat
   ```

---

### Q5: Comment mettre à jour les dépendances ?

**A:**
```batch
call .venv\Scripts\activate.bat
pip install --upgrade -r config/requirements.txt
```

**Attention** : Ne pas upgrader NumPy au-delà de 1.x !

---

## 🎮 GPU & Performance

### Q6: Mon GPU n'est pas détecté

**A:** **Vérifications** :

1. **Vérifier CUDA/GPU disponibilité** :
   ```batch
   scripts\run_test.bat test_cuda
   ```

2. **Drivers NVIDIA à jour** :
   - Télécharger derniers drivers : [nvidia.com](https://www.nvidia.com/Download/index.aspx)

3. **PyTorch avec CUDA** :
   ```batch
   python -c "import torch; print(torch.cuda.is_available())"
   # Doit afficher: True
   ```

4. **Réinstaller PyTorch GPU** :
   ```batch
   pip uninstall torch torchvision torchaudio
   
   # CUDA 12.4 (RTX 40xx/50xx)
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   
   # CUDA 11.8 (RTX 30xx)
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

---

### Q7: Quelle carte graphique minimum ?

**A:** **Recommandations** :

| GPU | VRAM | YOLOv8 | Use Case |
|-----|------|--------|----------|
| **GTX 1050 Ti** | 4 GB | n/s | Test, learning |
| **RTX 3060** | 12 GB | n/s/m | Production (recommandé) |
| **RTX 3080** | 10 GB | n/s/m/l | High-end |
| **RTX 4090** | 24 GB | Tous | Maximum performance |
| **CPU Only** | - | n | Fallback (lent) |

**Sans GPU** : Tout fonctionne sur CPU (10-20× plus lent).

---

### Q8: Out of Memory (OOM) pendant training

**A:** **Solutions** :

1. **Réduire batch size** :
   - GUI : Training tab → Batch Size : 16 → 8 ou 4
   - CLI : `--batch 8`

2. **Réduire image size** :
   - GUI : Training tab → Image Size : 640 → 512 ou 320
   - CLI : `--imgsz 512`

3. **Utiliser modèle plus petit** :
   - YOLOv8x → YOLOv8n (68M → 3M params)

4. **Activer cache=False** :
   - Désactive cache RAM images
   - Settings → Training → Cache : False

5. **Forcer CPU** (dernier recours) :
   - Settings → Debug → Device : CPU Only

---

### Q9: FPS très bas en détection webcam

**A:** **Optimisations** :

1. **Utiliser YOLOv8n** (modèle le plus rapide) :
   - Detection tab → Model : yolov8n.pt

2. **Réduire résolution webcam** :
   - Webcam Settings → Resolution : 640×480

3. **Augmenter confidence threshold** :
   - Detection tab → Confidence : 0.25 → 0.5
   - Réduit calculs post-processing

4. **Désactiver show_prices** :
   - Detection tab → Show Prices : Décoché
   - Économise lookups database

5. **Vérifier GPU utilisé** :
   ```batch
   scripts\run_test.bat test_cuda
   ```

**FPS attendus** :

| GPU | YOLOv8n | YOLOv8m |
|-----|---------|---------|
| **RTX 3060** | 45-60 FPS | 25-35 FPS |
| **RTX 3080** | 60+ FPS | 40-50 FPS |
| **CPU i7** | 8-15 FPS | 3-5 FPS |

---

### Q10: Comment optimiser pour mon hardware ?

**A:** **Settings → Debug tab** :

1. **Workers** : Nombre threads
   - Auto-détection : Nombre cores CPU
   - RTX 3060 : 8-12 workers
   - i7 CPU : 4-8 workers

2. **Cache Mode** :
   - RAM : Images en mémoire (rapide, consomme RAM)
   - Disk : Cache sur disque SSD (économise RAM)
   - Disabled : Pas de cache (économise espace)

3. **Device** :
   - Auto : Détection auto GPU/CPU
   - CUDA 0 : Force GPU 0
   - CPU Only : Force CPU (debug)

---

## 🖼️ Dataset & Images

### Q11: Combien d'images minimum pour training ?

**A:** **Recommandations** :

| Objectif | Images/Classe | Total (10 classes) |
|----------|---------------|--------------------|
| **Test rapide** | 10-20 | 100-200 |
| **POC (Proof of Concept)** | 30-50 | 300-500 |
| **Production** | 100-200 | 1000-2000 |
| **Compétition** | 500+ | 5000+ |

**Astuce** : Utiliser augmentation pour multiplier dataset :
- 50 images × 20 augmentations = 1000 images

---

### Q12: Formats d'images supportés ?

**A:** **Supportés** :
- ✅ PNG (recommandé, alpha channel)
- ✅ JPG / JPEG
- ✅ BMP
- ✅ TIFF

**Non supportés** :
- ❌ GIF animés
- ❌ SVG vectoriels
- ❌ WebP

**Conversion** :
```python
from PIL import Image
img = Image.open('card.webp')
img.save('card.png')
```

---

### Q13: Taille d'image recommandée ?

**A:** **Optimal pour YOLO** :
- **640×640 pixels** (standard)
- **512×512** (économie VRAM)
- **1280×1280** (haute précision, VRAM++)

**Cartes Pokémon TCG** :
- Format original : 488×680 pixels
- Redimensionné auto par YOLO

**Conseil** : Ne pas redimensionner manuellement, YOLO gère.

---

### Q14: Images corrompues détectées

**A:** **Vérifier corruption** :
```batch
scripts\run_test.bat check_corrupted_images
```

**Output** : Liste images corrompues dans logs

**Solutions** :
1. **Supprimer images corrompues**
2. **Réessayer téléchargement** (si TCGdex)
3. **Convertir formats** (PNG → JPG)

**Auto-clean pendant génération mosaïques** :
- Mosaïques auto-déplace corrupted/ vers dossier `corrupted/`

---

### Q15: Puis-je utiliser mes propres images ?

**A:** **Oui !** 3 options :

**Option 1 : Placer dans `images/`**
```
images/
  └── my_cards/
      ├── card1.png
      ├── card2.png
      └── ...
```

**Option 2 : Télécharger depuis TCGdex API**
- Image Download tab → Sélection set → Download

**Option 3 : Workflow complet custom**
1. Créer dossier `images/my_set/`
2. Copier images dedans
3. Lancer Workflow avec ce dossier

**Annotations nécessaires** : Labels YOLO `.txt` (générés auto par mosaics)

---

## 🎨 Augmentation

### Q16: Combien d'augmentations par image ?

**A:** **Dépend du dataset initial** :

| Dataset | Augmentations | Total |
|---------|---------------|-------|
| 50 images | 20 | 1000 images |
| 100 images | 10 | 1000 images |
| 500 images | 2-5 | 1000-2500 images |

**Limite** : 20 augmentations/image (configurable)

**GUI** : Augmentation tab → Count : 1-20

---

### Q17: Augmentation trop lente (2-5 sec/image)

**A:** **Normal avec imgaug** :

**Performance attendue** :
- CPU i7 : 2-3 sec/image
- CPU i9 : 1-2 sec/image
- GPU : imgaug GPU expérimental (pas utilisé)

**Optimisations** :
1. **Réduire techniques actives** :
   - Settings → Augmentation → Décocher techniques inutiles
   
2. **Activer workers** :
   - Settings → Debug → Workers : 8-12
   - Parallélisation CPU

3. **Utiliser batch** :
   - Génération par batch (automatique)

**Estimation** :
- 100 images × 10 augmentations = 1000 images → 30-50 min

---

### Q18: Quelles techniques d'augmentation choisir ?

**A:** **Recommandations par catégorie** :

**Toujours activer (essentielles)** :
- ✅ Brightness (-50 à +50)
- ✅ Rotation (±15°)
- ✅ Flip Horizontal
- ✅ Gaussian Blur (σ 0-2)

**Selon use case** :
- 📸 Photos webcam : Noise, Motion Blur
- 🌟 Cartes holographiques : Holographic augmentation
- 📦 Scans : CLAHE, Sharpen

**Éviter si problématique** :
- ⚠️ Perspective (si cartes très déformées)
- ⚠️ Elastic Transform (si artefacts visuels)

---

### Q19: Différence Standard vs Holographic augmentation ?

**A:**

| Type | Techniques | Output | Durée |
|------|-----------|--------|-------|
| **Standard** | 22 imgaug (géométrique, couleur, blur) | Cartes normales | 30-60 min (1000 img) |
| **Holographic** | 5 styles (Rainbow, Metallic, Glitter, Prismatic, Sparkle) | Cartes shiny | 5-10 min (v3.2.2 optimisé 100-300×) |

**Workflow recommandé** :
1. Standard augmentation (×10)
2. Puis Holographic (×3-5 styles)

**Total** : 50 images → 500 standard + 150 holographic = 650 images

---

## 🧩 Mosaïques

### Q20: Quelle est la différence entre Quick/Standard/Complete ?

**A:**

| Mode | Mosaïques | Cartes/Mosaïque | Durée (v3.2.1) | Use Case |
|------|-----------|-----------------|----------------|----------|
| **Quick** | ~200 | 2-4 | 2-3 min | Test rapide |
| **Standard** | ~500 | 4-6 | 5-8 min | Production (recommandé) |
| **Complete** | Toutes | 6-8 | 10-15 min | Maximum dataset |

**Complete mode** : Génère TOUTES combinaisons possibles depuis images disponibles.

**Exemple** :
- 50 cartes, mode Standard → ~500 mosaïques
- 100 cartes, mode Complete → 1000-2000 mosaïques

---

### Q21: Mosaïques floues ou pixelisées

**A:** **Causes possibles** :

1. **Images source basse résolution**
   - TCGdex : 512×710 pixels (optimal)
   - Si < 200×200 : Trop petit

2. **Background web basse qualité**
   - Solution : Utiliser Local backgrounds
   - Placer images haute-res dans `backgrounds/`

3. **PNG compression**
   - v3.2.1 : compression=0 (désactivé par défaut)
   - Pas de perte qualité

**Vérification** :
```batch
scripts\run_test.bat test_project_integrity
```

---

### Q22: Annotations YOLO manquantes

**A:** **Vérifier présence labels** :

```batch
scripts\run_test.bat verify_data_yaml
```

**Structure attendue** :
```
output/mosaics/
  ├── images/
  │   └── L1_B0_T0_layout_001.png
  └── labels/
      └── L1_B0_T0_layout_001.txt  # Même nom !
```

**Contenu `.txt`** (format YOLO) :
```
0 0.5 0.5 0.3 0.4  # class x_center y_center width height
1 0.2 0.3 0.3 0.4
```

**Si labels manquants** :
- Régénérer mosaïques
- Vérifier logs pour erreurs

---

### Q23: Mosaics generation échoue avec "No images found"

**A:** **Vérifier chemin images** :

1. **Vérifier images disponibles** :
   - GUI : Dashboard → Total Images > 0 ?
   - Dossier : `images/` ou `images/surging_sparks/`

2. **Vérifier configuration** :
   - Settings → Mosaic → Input Directory

3. **Relancer téléchargement** :
   - Image Download tab → Sélectionner set → Download

---

### Q24: Corrupted images détectées pendant mosaics

**A:** **Auto-handling v3.2.1** :

**Comportement** :
- Images corrompues auto-déplacées vers `corrupted/`
- Génération continue sans crash
- Logs affichent images corrompues

**Vérifier** :
```batch
scripts\run_test.bat check_corrupted_images
```

**Nettoyage** :
```batch
rmdir /s /q corrupted\
```

---

### Q25: Comment personnaliser les backgrounds ?

**A:** **3 sources backgrounds** :

**1. Fake Cards (défaut)** :
- Générés avec Perlin noise
- Fakeimg/ directory

**2. Local** :
- Placer images dans `backgrounds/`
- Formats : PNG, JPG, BMP
- Résolution recommandée : 640×640

**3. Web** :
- Téléchargement automatique depuis Unsplash/Pexels
- Requiert connexion internet

**Configuration** :
- GUI : Mosaic tab → Background : Local
- Settings : `gui_config.json` → mosaic.background

---

## 🎓 Entraînement YOLO

### Q26: Quel modèle YOLO choisir ?

**A:** **Comparaison YOLOv8** :

| Modèle | Params | VRAM | mAP | FPS (RTX 3060) | Use Case |
|--------|--------|------|-----|----------------|----------|
| **n** | 3.2M | 2 GB | 37% | 60+ | Mobile, real-time |
| **s** | 11.2M | 4 GB | 44% | 45 | Production (recommandé) |
| **m** | 25.9M | 6 GB | 50% | 30 | Haute précision |
| **l** | 43.7M | 8 GB | 53% | 20 | Maximum précision |
| **x** | 68.2M | 12 GB | 54% | 15 | Compétition |

**YOLO11 (nouveau 2024)** :
- **n** : 2.6M params (plus léger que YOLOv8n)
- **s** : 9.4M params
- Amélioration 5-10% mAP vs YOLOv8

**Recommandation générale** : **YOLOv8s** (équilibre vitesse/précision)

---

### Q27: Training bloqué à 0% ou très lent

**A:** **Causes possibles** :

1. **Dataset trop grand** :
   - 10,000 images × 100 epochs = 12-24h
   - Solution : Réduire epochs (50) ou dataset (1000 images)

2. **Cache loading** :
   - Premier epoch : Cache images en RAM (lent)
   - Epochs suivants : Rapide

3. **CPU training** :
   - GPU pas détecté → 10-20× plus lent
   - Vérifier : `scripts\run_test.bat test_cuda`

4. **Batch size trop petit** :
   - batch=1 → Très lent
   - Augmenter : batch=8 ou 16

**Progression normale** :
- Epoch 1 : 10-15 min (cache loading)
- Epochs suivants : 3-5 min/epoch

---

### Q28: Validation mAP très bas (<10%)

**A:** **Causes possibles** :

1. **Epochs insuffisants** :
   - 10 epochs : Sous-entraîné
   - Minimum : 50 epochs
   - Recommandé : 100-200 epochs

2. **Dataset déséquilibré** :
   - Classe A : 500 images, Classe B : 10 images
   - Solution : Auto-balancer (`target=50`)

3. **Annotations incorrectes** :
   - Vérifier : `scripts\run_test.bat verify_data_yaml`
   - Valider : Validation tab

4. **Learning rate trop élevé** :
   - Défaut : 0.01 (optimal)
   - Réduire : 0.001

5. **Augmentation insuffisante** :
   - 50 images × 2 augmentations = 100 (trop peu)
   - Recommandé : 50 × 10 = 500

**mAP attendu** :
- 50 epochs, 500 images : 40-50%
- 100 epochs, 1000 images : 55-65%
- 200 epochs, 2000 images : 65-75%

---

### Q29: Comment reprendre training interrompu ?

**A:** **Utiliser checkpoint `last.pt`** :

```batch
call .venv\Scripts\activate.bat
python -m ultralytics.models.yolo.detect.train resume \
  model=runs/detect/train/weights/last.pt
```

**Via GUI** :
- Training tab → Model : `runs/detect/train/weights/last.pt`
- Cocher "Resume Training"
- START TRAINING

**YOLO gère** :
- Reprend à l'epoch interrompu
- Conserve optimizer state
- Continue métriques

---

### Q30: Training terminé mais best.pt inexistant

**A:** **Vérifier chemins** :

**Chemin standard** :
```
runs/detect/train/weights/best.pt
```

**Si dossiers multiples** :
```
runs/detect/train2/weights/best.pt
runs/detect/train3/weights/best.pt
```

**Dernière version** :
```batch
dir /b /o-d runs\detect\
# Affiche dossiers par date (le plus récent en premier)
```

**Si vraiment absent** :
- Training a crashé avant fin
- Vérifier logs : `runs/detect/train/results.csv`
- Utiliser `last.pt` comme fallback

---

## 🔍 Détection

### Q31: Aucune détection en mode webcam/video

**A:** **Checklist** :

1. **Modèle chargé ?**
   - Detection tab → Model : `runs/.../best.pt` ou `yolov8n.pt`

2. **Confidence threshold trop haut ?**
   - Detection tab → Confidence : 0.25 (défaut)
   - Réduire : 0.1 (détecte plus)

3. **Webcam connectée ?**
   - Webcam ID : 0 (défaut), essayer 1 ou 2
   - Test : Windows Camera app

4. **Distance caméra-carte** :
   - Trop loin : Carte < 10% de l'image
   - Optimal : Carte occupe 30-50% de l'image

5. **Éclairage** :
   - Trop sombre : Détection difficile
   - Optimal : Lumière naturelle diffuse

**Test simple** :
- Detection → Image File
- Sélectionner image test
- Si détection OK : Problème webcam
- Si pas de détection : Problème modèle

---

### Q32: Détections multiples sur une seule carte (overlaps)

**A:** **Ajuster IoU threshold** :

**IoU (Intersection over Union)** : Seuil chevauchement accepté

**Configuration** :
- Detection tab → IoU Threshold : 0.45 (défaut)
- Augmenter : 0.6-0.8 (réduit overlaps)

**Exemple** :
- IoU = 0.3 : Accepte 30% overlap → Beaucoup de détections
- IoU = 0.7 : Accepte 70% overlap → Supprime duplicatas

**NMS (Non-Maximum Suppression)** : YOLO garde meilleure détection

---

### Q33: FPS faible en détection temps réel

**A:** **Voir Q9 (GPU & Performance)** ci-dessus.

**Résumé optimisations** :
- ✅ YOLOv8n (modèle le plus rapide)
- ✅ Réduire résolution webcam (640×480)
- ✅ Confidence = 0.5 (réduit post-processing)
- ✅ Désactiver show_prices
- ✅ GPU CUDA activé

---

### Q34: Prix ne s'affichent pas sur détections

**A:** **Vérifications** :

1. **Show Prices activé ?**
   - Detection tab → Show Prices : ✅ Coché

2. **Base de données prix existe ?**
   - Vérifier : `models/cards_database.yaml`
   - Si absent : Initialiser prix (`scripts\run_script.bat init_prices`)

3. **Mapping class_id → card_name** :
   - Vérifier : `models/card_name_to_id.json`
   - Si absent : Créer mapping

4. **Prix dans database ?**
   - Ouvrir `cards_database.yaml`
   - Vérifier champ `price:` et `price_max:`

**Initialisation complète** :
```batch
# Créer mapping
scripts\run_script.bat create_card_mapping

# Initialiser prix
scripts\run_script.bat init_prices
```

---

### Q35: Comment sauvegarder détections annotées ?

**A:** **3 méthodes** :

**1. Screenshot pendant détection webcam** :
- Appuyer sur **'s'** pendant détection
- Sauvegarde dans `screenshots/<timestamp>.jpg`

**2. Video file mode** :
- Detection → Video File
- Sélectionner vidéo input
- Output automatique : `output_annotated.mp4`

**3. Batch image detection** :
- Detection → Image File (boucle)
- Sélectionner dossier images
- Outputs dans `output_annotated/`

---

## 💰 Prix & TCGdex API

### Q36: TCGdex API ne répond pas

**A:** **Vérifications** :

1. **Connexion internet** :
   ```batch
   ping api.tcgdex.net
   ```

2. **API status** :
   - Vérifier : [status.tcgdex.net](https://status.tcgdex.net)

3. **Rate limiting** :
   - TCGdex limite : 100 req/min
   - Solution : Attendre 1 min, retry

4. **Firewall/Proxy** :
   - Vérifier firewall Windows
   - Essayer sans VPN

**Fallback manuel** :
- Créer `cards_database.yaml` manuellement
- Format :
```yaml
cards:
  - name: "Pikachu"
    id: "sv08_001"
    price: 2.50
    price_max: 5.00
```

---

### Q37: Prix en EUR ou USD ?

**A:** **2 sources disponibles** :

| Source | Devise | API | Fiabilité |
|--------|--------|-----|-----------|
| **Cardmarket** | EUR | TCGdex | Haute (Europe) |
| **TCGPlayer** | USD | TCGdex | Haute (US) |

**Configuration** :
```json
// api_config.json
{
  "price_source": "cardmarket",  // ou "tcgplayer"
  "currency": "EUR"               // ou "USD"
}
```

**GUI** : Settings → Export → Price Source

---

### Q38: Comment mettre à jour les prix régulièrement ?

**A:** **3 options** :

**1. Mise à jour manuelle** :
```batch
scripts\run_script.bat init_prices
```

**2. Mise à jour automatique** (via GUI) :
- Tools → Excel & Prices → Update Prices

**3. Automatisation (Windows Task Scheduler)** :
```batch
# Créer tâche planifiée
# Commande :
C:\DATA\pok\.venv\Scripts\python.exe C:\DATA\pok\scripts\init_prices.py
# Récurrence : Hebdomadaire
```

---

### Q39: Migration Excel → YAML

**A:** **Pourquoi YAML ?**
- ✅ Plus léger (50% moins d'espace)
- ✅ Lisible humain
- ✅ Git-friendly (diff)
- ✅ Pas de dépendance openpyxl

**Migration** :
```batch
scripts\run_script.bat convert_excel_to_yaml
```

**Input** : `excel/cards_with_prices.xlsx`
**Output** : `models/cards_database.yaml`

**Vérification** :
```batch
python -c "import yaml; print(yaml.safe_load(open('models/cards_database.yaml')))"
```

---

## ⚠️ Erreurs Courantes

### Q40: "RuntimeError: CUDA out of memory"

**A:** **Voir Q8 (Out of Memory)** ci-dessus.

**Résumé solutions** :
1. Réduire batch size (16 → 8 → 4)
2. Réduire image size (640 → 512)
3. Modèle plus petit (YOLOv8m → YOLOv8n)
4. Désactiver cache RAM
5. Forcer CPU (fallback)

---

### Q41: "ModuleNotFoundError: No module named 'imgaug'"

**A:** **Environnement virtuel pas activé**.

**Solution** :
```batch
call .venv\Scripts\activate.bat
pip install imgaug
```

**OU** :
```batch
# Réinstaller tout
INSTALL.bat
```

---

### Q42: "FileNotFoundError: data.yaml not found"

**A:** **Dataset YOLO pas créé**.

**Solution** :
1. Générer mosaïques (créé `output/mosaics/`)
2. `data.yaml` généré automatiquement

**OU créer manuellement** :
```yaml
# output/mosaics/data.yaml
train: output/mosaics/train/images
val: output/mosaics/val/images
nc: 10  # Nombre classes
names: ['class_0', 'class_1', ...]
```

---

### Q43: "UnicodeEncodeError" dans logs Windows

**A:** **Caractères spéciaux (accents, emojis) non supportés par console Windows**.

**Solution automatique** :
- `core/utils.py` → `safe_print()` gère Unicode
- Remplace print() standard

**Solution manuelle** :
```python
# Dans scripts
from core.utils import safe_print
safe_print("✅ Génération terminée")  # OK
```

**Variables d'environnement** :
```batch
set PYTHONIOENCODING=utf-8
python mon_script.py
```

---

### Q44: "Permission denied" lors suppression fichiers

**A:** **Fichier ouvert dans autre programme**.

**Solutions** :
1. **Fermer programmes** :
   - Explorateur Windows (preview)
   - Éditeurs d'image
   - Viewers PDF

2. **Redémarrer GUI** :
   - Fichiers verrouillés par GUI
   - Fermer START.bat → Relancer

3. **Forcer suppression** (Admin) :
```batch
# Lancer CMD en Administrateur
rmdir /s /q output\
```

---

### Q45: Interface GUI freeze/bloque

**A:** **Opération longue en cours**.

**Causes** :
- Augmentation 1000 images (30-60 min)
- Training 100 epochs (2-8h)
- Validation large dataset (10-20 min)

**Solutions** :
1. **Attendre fin** : Vérifier logs console
2. **Vérifier CPU/GPU usage** : Task Manager
3. **Forcer quit** : Ctrl+C dans console (perd progression)

**Amélioration future** : Threads GUI séparés (en cours)

---

### Q46: "ValueError: Invalid YOLO format"

**A:** **Labels YOLO mal formatées**.

**Format YOLO attendu** :
```
class_id x_center y_center width height
0 0.5 0.5 0.3 0.4
```

**Valeurs attendues** :
- `class_id` : Entier ≥ 0
- `x_center, y_center, width, height` : Float [0.0, 1.0]

**Validation** :
```batch
scripts\run_test.bat verify_data_yaml
```

**Correction manuelle** :
- Ouvrir `.txt` label file
- Vérifier format ligne par ligne
- Supprimer lignes invalides

---

### Q47: YOLOv11 non disponible

**A:** **Ultralytics version < 8.3.0**.

**Mise à jour** :
```batch
call .venv\Scripts\activate.bat
pip install --upgrade ultralytics
```

**Vérifier version** :
```batch
python -c "import ultralytics; print(ultralytics.__version__)"
# Doit afficher : 8.3.0+
```

**Compatibilité** :
- YOLOv8 : ultralytics ≥ 8.0.0
- YOLO11 : ultralytics ≥ 8.3.0

---

### Q48: Imports extrêmement lents au démarrage

**A:** **Imports PyTorch/OpenCV lourds (normal)**.

**Première exécution** :
- Chargement DLLs CUDA : 10-30 sec
- Initialisation GPU : 5-10 sec

**Exécutions suivantes** : Plus rapide (cache OS)

**Optimisations** :
1. **SSD recommandé** (vs HDD)
2. **Antivirus** : Exclure dossier projet
3. **Windows Defender** : Exclure `.venv/`

**Benchmark** :
```batch
scripts\run_test.bat test_import_speed
```

---

### Q49: "Killed" ou crash sans message d'erreur

**A:** **Out of RAM (système kill process)**.

**Vérifier RAM** : Task Manager → Performance

**Causes** :
- Cache 10,000 images en RAM
- Training batch size trop élevé
- Workers trop nombreux

**Solutions** :
1. **Réduire cache** :
   - Settings → Debug → Cache : Disk ou Disabled

2. **Réduire workers** :
   - Settings → Debug → Workers : 4 (vs 12)

3. **Réduire batch** :
   - Training → Batch Size : 8 (vs 16)

4. **Fermer programmes** : Libérer RAM

---

### Q50: Git push refuse (fichiers trop gros)

**A:** **Fichiers modèles/datasets trop gros pour GitHub**.

**GitHub limits** :
- Fichier : 100 MB max
- Push : 2 GB max

**Fichiers problématiques** :
- `yolov8x.pt` : 136 MB ❌
- `runs/detect/train/` : 500+ MB ❌
- `images/` : 1-5 GB ❌

**Solutions** :

**1. Utiliser `.gitignore` (recommandé)** :
```gitignore
# Déjà dans .gitignore
runs/
images/
output/
*.pt
```

**2. Git LFS (Large File Storage)** :
```batch
git lfs install
git lfs track "*.pt"
git add .gitattributes
git commit -m "Add LFS tracking"
```

**3. Exclure manuellement** :
```batch
git rm --cached runs/ -r
git commit -m "Remove training runs"
```

---

## 🔄 Workflow

### Q51: Workflow automatique échoue à mi-chemin

**A:** **Vérifier logs pour étape en échec**.

**Étapes Workflow** :
1. Augmentation
2. Holographic (optionnel)
3. Mosaics
4. Validation + Balance
5. Training (optionnel)

**Échec courant : Étape 3 (Mosaics)** :
- Images insuffisantes (< 10)
- Corrupted images
- Solution : Voir Q14, Q24

**Reprise manuelle** :
- Désactiver étapes terminées
- Relancer Workflow

---

### Q52: Combien de temps pour un workflow complet ?

**A:** **Estimation par configuration** :

| Configuration | Images | Augmentations | Mosaics | Training | Total |
|---------------|--------|---------------|---------|----------|-------|
| **Quick Test** | 50 | 5 | Quick | Non | 1h |
| **POC** | 100 | 10 | Standard | 50 epochs | 4-6h |
| **Production** | 500 | 10 | Complete | 100 epochs | 8-12h |
| **Competition** | 1000 | 20 | Complete | 200 epochs | 20-30h |

**Détails (Production)** :
- Téléchargement (500 cartes) : 15-25 min
- Augmentation (500 × 10 = 5000) : 2-3h
- Holographic (optionnel) : 10-15 min
- Mosaics (500 Complete) : 10-15 min
- Validation + Balance : 20-30 min
- Training (100 epochs) : 3-5h

**GPU recommandé** : RTX 3060+ (sinon 2-3× plus lent)

---

### Q53: Peut-on arrêter et reprendre workflow ?

**A:** **Non, workflow ne supporte pas reprise automatique**.

**Solutions** :

**1. Désactiver étapes terminées** :
- Workflow tab → Décocher étapes finies
- Relancer

**2. Exécution manuelle par étape** :
- Augmentation tab → Générer
- Mosaics tab → Générer
- Training tab → Entraîner

**3. Scripts CLI** :
```batch
# Étape par étape
call .venv\Scripts\activate.bat
python core/augmentation.py --count 10
python core/mosaic_optimized.py 1 0 0
python core/training_manager.py --epochs 50
```

---

### Q54: Workflow génère trop d'images (espace disque)

**A:** **Configurer limites** :

**Augmentation** :
- Count : 10 → 5 (réduit 50%)

**Mosaics** :
- Mode : Complete → Standard (réduit 50%)

**Nettoyage régulier** :
- Tools → Clean & Reset → Clean Output

**Estimation espace** :

| Élément | Taille/Image | Total (500 cartes) |
|---------|--------------|---------------------|
| Images sources | 500 KB | 250 MB |
| Augmented (×10) | 500 KB | 2.5 GB |
| Mosaics (500) | 800 KB | 400 MB |
| Training runs | - | 500 MB |
| **TOTAL** | - | **3.6 GB** |

---

### Q55: Comment partager mon dataset YOLO ?

**A:** **3 méthodes** :

**1. Export Roboflow** :
- Export tab → Format : Roboflow
- Upload sur [roboflow.com](https://roboflow.com)
- Partage lien

**2. Archive ZIP** :
```batch
# Compresser
powershell Compress-Archive output/mosaics dataset.zip
```

**3. GitHub release** :
- Commit dataset (si < 2 GB)
- Tag release : `v1.0.0`
- Attach `dataset.zip`

**Structure à inclure** :
```
dataset/
  ├── images/
  ├── labels/
  ├── data.yaml
  └── README.md (description)
```

---

### Q56: Puis-je utiliser plusieurs GPUs ?

**A:** **Support multi-GPU limité**.

**Configuration** :
- Settings → Debug → Device : CUDA 0 / CUDA 1

**YOLO multi-GPU** (expérimental) :
```python
# Via code
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.train(data='data.yaml', device=[0, 1])  # GPU 0 + GPU 1
```

**Limitation** :
- Augmentation : 1 GPU uniquement
- Training : Multi-GPU supporté (DataParallel)
- Detection : 1 GPU uniquement

---

### Q57: Comment benchmarker mon setup ?

**A:** **Tests disponibles** :

**Performance** :
```batch
scripts\run_test.bat test_mosaic_performance
scripts\run_test.bat test_holographic_performance
```

**GPU** :
```batch
scripts\run_test.bat test_cuda
```

**Intégrité** :
```batch
scripts\run_test.bat test_project_integrity
```

**Tous les tests** :
```batch
scripts\run_all_tests.bat
```

**Outputs** : Métriques dans logs console

---

### Q58: Erreur "data.yaml: nc mismatch"

**A:** **Nombre de classes (nc) ne correspond pas**.

**Vérifier `data.yaml`** :
```yaml
nc: 10  # Doit correspondre au nombre réel de classes
names: ['class_0', 'class_1', ..., 'class_9']  # 10 classes
```

**Solution** :
1. Compter classes réelles dans dataset
2. Mettre à jour `nc:` dans data.yaml
3. Vérifier liste `names:` (doit avoir `nc` éléments)

---

### Q59: Licence et usage commercial ?

**A:** **Projet Open Source**.

**Licence** : MIT (à confirmer dans LICENSE file)

**Usage autorisé** :
- ✅ Personnel
- ✅ Éducatif
- ✅ Commercial (avec attribution)

**Dépendances** :
- YOLO (Ultralytics) : AGPL-3.0 (commercial license disponible)
- imgaug : MIT
- OpenCV : Apache 2.0

**Datasets TCGdex** : Respecter [ToS TCGdex](https://www.tcgdex.net/terms)

---

### Q60: Où trouver de l'aide supplémentaire ?

**A:** **Ressources** :

**Documentation** :
- `docs/README_COMPLET.md` : Guide complet
- `docs/HELP.md` : Aide générale
- `docs/FEATURES.md` : Liste fonctionnalités

**Tests & Scripts** :
- `scripts/SCRIPTS_REFERENCE.py` : Liste tous scripts disponibles

**Issues GitHub** :
- [github.com/username/pok/issues](https://github.com) (à adapter)

**Communautés** :
- Ultralytics Discord : [discord.com/invite/ultralytics](https://discord.com/invite/ultralytics)
- YOLO Forums : [community.ultralytics.com](https://community.ultralytics.com)

**Logs** :
- Console logs dans `START.bat` window
- Debug logs : Settings → Debug → Save Debug Logs

---

**Dernière mise à jour** : 14 novembre 2025  
**Version** : 3.2

**N'hésitez pas à contribuer** :
- Signaler bugs : GitHub Issues
- Proposer features : Pull Requests
- Améliorer docs : Editer markdown files
