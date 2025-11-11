# 📋 Guide de Migration : Excel → YAML

**Date** : 11 novembre 2025  
**Version** : 1.0  
**Objectif** : Migrer de `excel/cards_info.xlsx` vers `models/cards_database.yaml`

---

## 🎯 Pourquoi migrer vers YAML ?

### Avantages

| Aspect | Excel (ancien) | YAML (nouveau) |
|--------|---------------|----------------|
| **Taille** | ~50KB + deps 50MB | ~10KB + dep 1MB |
| **Lisibilité** | ❌ Format binaire | ✅ Texte clair |
| **Édition** | Excel requis | ✅ N'importe quel éditeur |
| **Git diff** | ❌ Binaire illisible | ✅ Diff ligne par ligne |
| **Performance** | Lent (pandas) | ✅ Rapide (yaml) |
| **Dépendances** | pandas + openpyxl | ✅ pyyaml seulement |

### Compatibilité

- ✅ **Backward compatible** : L'ancien Excel fonctionne toujours
- ✅ **Auto-détection** : Le code détecte automatiquement YAML ou Excel
- ✅ **Migration facile** : Script automatique fourni

---

## 🚀 Migration automatique (Recommandé)

### Méthode 1 : Script de migration

```bash
# Depuis la racine du projet
scripts\run_script.bat migrate_excel_to_yaml
```

**Ce script va** :
1. ✅ Créer un backup de `excel/cards_info.xlsx` → `excel/cards_info_backup.xlsx`
2. ✅ Lire toutes les cartes depuis Excel
3. ✅ Convertir en format YAML
4. ✅ Sauvegarder dans `models/cards_database.yaml`
5. ✅ Conserver les prix existants

**Résultat** :
- Nouveau fichier : `models/cards_database.yaml`
- Backup : `excel/cards_info_backup.xlsx`
- Ancien Excel : `excel/cards_info.xlsx` (conservé pour référence)

---

## 📝 Migration manuelle

### Étape 1 : Créer la structure YAML

Créez `models/cards_database.yaml` :

```yaml
# models/cards_database.yaml

metadata:
  version: "1.0"
  format: "YOLO-compatible card database"
  last_updated: "2025-11-11"
  source: "Migration from Excel"
  total_cards: 8  # Ajuster selon votre nombre de cartes
  comment: "Bounding boxes are generated dynamically"

cards:
  sv08_019:
    name: "Exeggcute"
    set: "Surging Sparks"
    set_full: "019/191"
    type: "Pokemon"
    rarity: "Common"
    price: 0.15
    price_max: 0.25
    price_source: "TCGdex"
    last_updated: "2025-11-11"
  
  # ... autres cartes
```

### Étape 2 : Convertir vos données

**Format Excel ancien** :
```
Set #      | Name       | Prix  | Prix max
-----------|------------|-------|----------
sv08_019   | Exeggcute  | 0.15  | 0.25
sv08_020   | Exeggutor  | 0.30  | 0.50
```

**Format YAML nouveau** :
```yaml
cards:
  sv08_019:
    name: "Exeggcute"
    price: 0.15
    price_max: 0.25
  sv08_020:
    name: "Exeggutor"
    price: 0.30
    price_max: 0.50
```

### Étape 3 : Valider la structure

```bash
# Tester le chargement YAML
.\.venv\Scripts\python.exe -c "import yaml; data = yaml.safe_load(open('models/cards_database.yaml')); print(f'✅ {len(data[\"cards\"])} cartes chargées')"
```

---

## 🔄 Workflows post-migration

### Ajouter une nouvelle carte

**Avant (Excel)** :
1. Ouvrir Excel
2. Ajouter ligne
3. Sauvegarder

**Maintenant (YAML)** :
1. Ouvrir `models/cards_database.yaml` avec n'importe quel éditeur
2. Copier-coller une carte existante
3. Modifier les valeurs
4. Sauvegarder

```yaml
cards:
  nouvelle_carte:
    name: "Pikachu"
    set: "Base Set"
    set_full: "025/102"
    type: "Pokemon"
    rarity: "Common"
    price: null  # Sera mis à jour plus tard
    price_max: null
    price_source: ""
    last_updated: "2025-11-11"
```

### Mettre à jour les prix

**Méthode automatique (TCGdex API)** :
```bash
scripts\run_script.bat update_prices_yaml
```

**Méthode manuelle** :
1. Ouvrir `models/cards_database.yaml`
2. Modifier les valeurs `price` et `price_max`
3. Sauvegarder

```yaml
sv08_019:
  name: "Exeggcute"
  price: 0.20  # Modifié de 0.15 à 0.20
  price_max: 0.30
  last_updated: "2025-11-12"  # Mettre à jour la date
```

### Initialiser depuis data.yaml

Si vous avez déjà un `output/dataset/data.yaml` avec vos cartes YOLO :

```bash
# Générer cards_database.yaml depuis data.yaml
scripts\run_script.bat init_prices

# Ou version simplifiée (8 cartes d'entraînement)
scripts\run_script.bat init_prices_simple
```

---

## 🔧 Commandes utiles

### Vérifier le format YAML

```bash
# Python
.\.venv\Scripts\python.exe -c "import yaml; yaml.safe_load(open('models/cards_database.yaml'))"

# Validation complète
scripts\run_test.bat test_yaml_loading
```

### Comparer YAML vs Excel

```bash
# Compter cartes YAML
.\.venv\Scripts\python.exe -c "import yaml; data=yaml.safe_load(open('models/cards_database.yaml')); print(len(data['cards']))"

# Compter cartes Excel (si pandas installé)
.\.venv\Scripts\python.exe -c "import pandas as pd; df=pd.read_excel('excel/cards_info.xlsx'); print(len(df))"
```

### Backup et restauration

```bash
# Backup YAML
copy models\cards_database.yaml models\cards_database_backup.yaml

# Restaurer depuis backup
copy models\cards_database_backup.yaml models\cards_database.yaml
```

---

## ❓ FAQ

### Q: Dois-je supprimer mon ancien fichier Excel ?
**R:** Non, il est conservé automatiquement pour référence. Le code détecte automatiquement le YAML en priorité.

### Q: Et si je veux revenir à Excel ?
**R:** Supprimez ou renommez `models/cards_database.yaml`, le code utilisera automatiquement `excel/cards_info.xlsx`.

### Q: Les bounding boxes sont-elles stockées dans le YAML ?
**R:** Non, elles sont générées dynamiquement pendant la création des mosaïques/augmentations.

### Q: Le YAML est-il compatible avec Git ?
**R:** Oui ! C'est un des avantages majeurs. Git peut faire des diffs ligne par ligne.

### Q: Comment éditer le YAML ?
**R:** Avec n'importe quel éditeur de texte : VS Code, Notepad++, Sublime Text, même Notepad.

### Q: Les prix sont-ils obligatoires ?
**R:** Non, vous pouvez laisser `price: null` et `price_max: null`. Les scripts de mise à jour TCGdex peuvent les remplir automatiquement.

### Q: Quelle est la taille typique d'un fichier YAML ?
**R:** ~10-20 KB pour 100-200 cartes (vs ~50KB pour Excel + 50MB de dépendances).

---

## 🐛 Dépannage

### Erreur : "YAML file not found"

**Solution** :
```bash
# Créer un fichier YAML exemple
scripts\run_script.bat init_prices_simple
```

### Erreur : "Invalid YAML structure"

**Solution** :
1. Vérifier l'indentation (2 espaces, pas de tabs)
2. Vérifier les guillemets autour des chaînes avec caractères spéciaux
3. Valider avec : `python -c "import yaml; yaml.safe_load(open('models/cards_database.yaml'))"`

### Les prix ne s'affichent pas dans la GUI

**Solutions** :
1. Vérifier que `models/cards_database.yaml` existe
2. Vérifier que les prix ne sont pas `null`
3. Cocher "💰 Show Prices" dans la GUI

### Migration échoue

**Solutions** :
1. Vérifier que `excel/cards_info.xlsx` existe et n'est pas corrompu
2. Vérifier les colonnes : doit avoir "Set #" et "Name" minimum
3. Fermer Excel si le fichier est ouvert
4. Essayer migration manuelle (voir section ci-dessus)

---

## 📚 Ressources

- **Spécification YAML** : https://yaml.org/spec/1.2.2/
- **Documentation complète** : `docs/README_COMPLET.md`
- **Scripts disponibles** : `scripts/SCRIPTS_REFERENCE.py`
- **Tests** : `tests/test_yaml_loading.py`

---

## ✅ Checklist post-migration

- [ ] Fichier `models/cards_database.yaml` créé
- [ ] Backup Excel créé (`excel/cards_info_backup.xlsx`)
- [ ] Nombre de cartes identique (YAML vs Excel)
- [ ] Prix conservés correctement
- [ ] GUI démarre sans erreur
- [ ] Détection avec prix fonctionne
- [ ] Tests YAML passent (`test_yaml_loading.py`)

---

**Dernière mise à jour** : 11 novembre 2025  
**Auteur** : lo26lo + GitHub Copilot
