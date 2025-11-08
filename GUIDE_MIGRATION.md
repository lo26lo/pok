# 🎯 RÉORGANISATION DES RÉPERTOIRES - Guide Rapide

## 📊 SITUATION ACTUELLE

Vous avez actuellement **5 problèmes majeurs** dans la structure des dossiers :

1. ❌ **Confusion** : `augment/` vs `output/augmented/` (lequel pour quoi ?)
2. ❌ **Mélange** : `output/yolov8/` contient augmented + mosaics (impossible à séparer)
3. ❌ **Doublons** : `output/yolov8_test/` (copie inutile)
4. ❌ **Noms peu clairs** : `fakeimg/`, `fakeimg_augmented/` (c'est quoi ?)
5. ❌ **Pipeline invisible** : Impossible de suivre : source → holo → augment → mosaic

---

## ✅ SOLUTION PROPOSÉE

### Structure AVANT → APRÈS

```
AVANT (confus)                          APRÈS (clair)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
images/                    →            images/
augment/                   →            output/holographic/
fakeimg/                   →            backgrounds/original/
fakeimg_augmented/         →            backgrounds/augmented/
output/augmented/          →            output/augmented/
output/yolov8/ (MÉLANGE)   →            output/mosaics/ (seulement mosaics)
                           →            output/dataset/ (FINAL: tout)
output/yolov8_test/        →            (SUPPRIMÉ)
```

### Workflow clair

```
images/ (8 cartes)
  ↓
output/holographic/ (24 images)
  ↓
output/augmented/ (1200 images)
  ↓
output/mosaics/ (150-250 mosaics)
  ↓
output/dataset/ (FINAL: 1450 images pour training)
```

---

## 🚀 COMMENT MIGRER ?

### Option 1 : Automatique (Recommandé) ⚡

```powershell
# 1 commande, tout est fait automatiquement
python migrate_directories.py
```

**Ce que ça fait** :
- ✅ Backup automatique de tout
- ✅ Crée la nouvelle structure
- ✅ Déplace tous les fichiers au bon endroit
- ✅ Met à jour `gui_config.json`
- ✅ Génère un rapport détaillé

**Durée** : 2-3 minutes

---

### Option 2 : Manuelle (Si vous préférez contrôler)

Voir fichier `PLAN_ACTION_MIGRATION.md` pour les commandes détaillées.

**Durée** : 30-45 minutes

---

## ⚠️ IMPORTANT APRÈS LA MIGRATION

### Vous DEVEZ mettre à jour les scripts

**8 fichiers core** à modifier pour utiliser les nouveaux chemins :

1. `core/mosaic.py` → `output/mosaics/` au lieu de `output/yolov8/`
2. `core/augmentation.py` → option `--source holographic`
3. `core/holographic_augmenter.py` → default `output/holographic/`
4. `core/random_erasing.py` → `backgrounds/augmented/`
5. `core/workflow_manager.py` → `output/dataset/`
6. `core/training_manager.py` → `output/dataset/data.yaml`
7. `core/auto_balancer.py` → `output/dataset/`
8. `check_corrupted_images.py` → `output/dataset/`

**2 fichiers GUI** :
- `GUI_v3.1_modern.py` → nouveaux chemins par défaut
- `gui_config.json` → déjà fait par `migrate_directories.py`

📄 **Liste complète des modifications** : Voir `PLAN_ACTION_MIGRATION.md` (Section Phase 2)

---

## 📦 NOUVEAU : Script de fusion du dataset

Après migration, utilisez ce script pour créer le dataset final :

```powershell
python merge_dataset.py
```

**Ce que ça fait** :
- Fusionne `output/augmented/` + `output/mosaics/` → `output/dataset/`
- Crée split train/val (80/20)
- Génère `data.yaml` pour YOLO
- Prêt pour entraînement

---

## ✅ VALIDATION

Après migration et mise à jour des scripts, testez :

```powershell
# 1. Test holographic
python core/holographic_augmenter.py images --output output/holographic

# 2. Test augmentation
python core/augmentation.py --num_aug 5

# 3. Test mosaic
python core/mosaic.py 1 0 0 --max-groups 10

# 4. Créer dataset final
python merge_dataset.py

# 5. Vérifier dataset
Get-ChildItem output/dataset/images | Measure-Object
Get-ChildItem output/dataset/labels | Measure-Object
```

---

## 🎯 AVANTAGES DE LA NOUVELLE STRUCTURE

| Avant | Après |
|-------|-------|
| ❌ Confusion sur les chemins | ✅ Chaque étape clairement identifiée |
| ❌ Fichiers mélangés | ✅ Séparation augmented / mosaics |
| ❌ Doublons inutiles | ✅ Plus de duplication |
| ❌ Pipeline invisible | ✅ Workflow traçable |
| ❌ Maintenance difficile | ✅ Facile à comprendre et modifier |

---

## 📚 DOCUMENTATION COMPLÈTE

1. **`ANALYSE_REPERTOIRES.md`** : Analyse détaillée + structure proposée
2. **`PLAN_ACTION_MIGRATION.md`** : Guide complet étape par étape
3. **`migrate_directories.py`** : Script de migration automatique
4. **`merge_dataset.py`** : Script de fusion du dataset final

---

## 🆘 AIDE

### Je veux juste tester sans tout casser

```powershell
# Test sur une copie
Copy-Item -Recurse pok pok_test
cd pok_test
python migrate_directories.py
# Testez, si ça marche, appliquez sur pok/
```

### J'ai un problème, comment revenir en arrière ?

Le script `migrate_directories.py` crée un backup automatique : `backup_YYYYMMDD_HHMMSS/`

```powershell
# Restaurer depuis le backup
$backup = "backup_20250108_143022"  # Remplacer par votre backup
Copy-Item -Recurse "$backup/*" . -Force
```

### Combien de temps ça prend ?

- **Migration automatique** : 2-3 minutes
- **Mise à jour scripts** : 1-2 heures (selon votre vitesse)
- **Tests de validation** : 30 minutes
- **Total** : ~2-3 heures

---

## 🚦 FEUILLE DE ROUTE

### Aujourd'hui (Étape 1)
1. Lire cette doc
2. Lire `ANALYSE_REPERTOIRES.md`
3. Décider : migration maintenant ou plus tard ?

### Si migration maintenant (Étape 2)
1. Lancer `python migrate_directories.py`
2. Vérifier le rapport : `migration_report.txt`
3. Tester la nouvelle structure

### Mise à jour scripts (Étape 3)
1. Suivre `PLAN_ACTION_MIGRATION.md` Phase 2
2. Modifier les 8 scripts core
3. Modifier GUI et config
4. Tester chaque script individuellement

### Validation finale (Étape 4)
1. Workflow complet de test (8 cartes)
2. Fusionner dataset : `python merge_dataset.py`
3. Entraîner modèle test (5 epochs)
4. Si OK → **Migration terminée ! 🎉**

---

## ❓ QUESTIONS FRÉQUENTES

**Q : Mes données actuelles seront-elles perdues ?**
R : Non, `migrate_directories.py` fait un backup complet avant toute modification.

**Q : Puis-je revenir en arrière ?**
R : Oui, à tout moment avec le backup.

**Q : Est-ce obligatoire ?**
R : Non, mais fortement recommandé pour :
- Éviter confusion future
- Faciliter la maintenance
- Clarifier le workflow
- Permettre l'ajout de nouvelles fonctionnalités

**Q : Ça va casser mon GUI actuel ?**
R : Temporairement oui, jusqu'à mise à jour de `GUI_v3.1_modern.py`. Le script de migration met déjà à jour `gui_config.json`.

**Q : Et mes 1350 images actuelles ?**
R : Elles sont migrées automatiquement :
- 1200 augmented → restent dans `output/augmented/`
- 150 mosaics → extraites vers `output/mosaics/`
- Fusion finale → `output/dataset/`

---

## 🎉 PRÊT À COMMENCER ?

```powershell
# Commande magique ✨
python migrate_directories.py
```

**Ensuite, suivez le plan dans `PLAN_ACTION_MIGRATION.md` pour mettre à jour les scripts.**

---

📝 **Note** : Gardez cette doc ouverte pendant la migration !
