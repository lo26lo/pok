# 🎮 Pokemon Dataset Generator v2.0 - Guide de Démarrage Rapide

## 🚀 Installation (Première utilisation)

### Étape 1 : Installer l'environnement
```batch
install_env.bat
```
Cela créera un environnement virtuel Python 3.12 avec toutes les dépendances nécessaires.

## ▶️ Lancement du GUI v2.0

```batch
run_gui_v2_with_env.bat
```

## ✨ Nouvelles Fonctionnalités v2.0

### 🔧 Menu Settings - Configuration des Chemins

**Accès :** Menu `Settings` → `Chemins et Configuration`

Vous pouvez maintenant personnaliser TOUS les chemins du projet :

- 📁 **Images Sources** : Dossier contenant vos cartes Pokemon originales
- 🖼️ **Fausses Cartes (fakeimg)** : Dossier pour les cartes avec Random Erasing
- 📤 **Sortie Augmentation** : Où sauvegarder les images augmentées
- 🧩 **Sortie Mosaïques** : Où sauvegarder les mosaïques YOLOv8
- 📊 **Fichier Excel** : Fichier cards_info.xlsx

**Comment modifier un chemin :**
1. Cliquer sur le bouton **📂** à côté du chemin
2. Sélectionner le dossier/fichier désiré
3. Cliquer **💾 Sauvegarder**

La configuration est sauvegardée automatiquement dans `gui_config.json`.

### 📊 Onglet Dashboard

**Statistiques en temps réel :**
- Nombre d'images sources
- Nombre de fausses cartes
- Nombre d'images augmentées
- Nombre de mosaïques générées

**Actions rapides :**
- 📁 Ouvrir les dossiers
- 📊 Ouvrir Excel
- 🗑️ Nettoyer Output
- ▶️ Workflow Complet (tout automatiser)

### 🎨 Onglet Augmentation

**Nouvelles fonctionnalités :**
- ✅ **Validation automatique** : Vérifie que les images sources existent
- ⚡ **Presets rapides** :
  - Rapide (5 augmentations)
  - Standard (15 augmentations)
  - Intensif (100 augmentations)
- 📊 Les paramètres sont mémorisés entre les sessions

### 🧩 Onglet Mosaïques

**Nouvelles fonctionnalités :**
- ✅ **Validation** : Vérifie que les images augmentées et fausses cartes existent
- 🎛️ Configuration complète des 3 modes :
  - Layout Mode (1: Grille, 2: Rotation forte, 3: Aléatoire)
  - Background Mode (0: Mosaïque, 1: Local, 2: Web)
  - Transform Mode (0: Rotation 2D, 1: 3D Perspective)

### 🖼️ Onglet Fausses Cartes ⭐ NOUVEAU

**Plus besoin de batch file séparé !** Tout est intégré dans le GUI :

- 🎚️ **Nombre de cartes** : Slider de 10 à 50
- ☑️ **Random Erasing** : Activer/Désactiver
- 🎚️ **Probabilité (p)** : Slider de 0.0 à 1.0
  - 0.0 = Aucune modification
  - 0.5 = Modification moyenne
  - 1.0 = Modification maximale

**Processus automatique :**
1. Copie aléatoire des cartes depuis Images Sources
2. Application du Random Erasing si activé
3. Sauvegarde dans le dossier fakeimg

### � Onglet Utilitaires ⭐ NOUVEAU

**Intégration complète de l'API Pokémon TCG !**

#### 📋 Générer Liste de Cartes depuis API
Récupère automatiquement toutes les cartes d'une extension :
- **Extension** : Nom de l'extension (ex: "Surging Sparks", "Obsidian Flames")
- **Sortie** : Nom du fichier Excel à générer
- **Résultat** : Fichier avec colonnes `Set #` (001/191) et `Name`
- **Utilité** : Créer rapidement un fichier de base pour votre collection

**Exemple :**
```
Extension: Surging Sparks
Sortie: surging_sparks.xlsx
→ Génère un fichier avec toutes les 191 cartes de l'extension
```

#### 💰 Mettre à Jour les Prix des Cartes
Met à jour les prix de marché TCGPlayer pour vos cartes :
- **Entrée** : Fichier Excel avec colonnes `Set #`, `Name`, `Set`
- **Sortie** : Nouveau fichier avec colonnes `Prix` et `Prix max` ajoutées
- **Parallélisé** : Traite plusieurs cartes simultanément (rapide!)
- **Résumé** : Liste des cartes où les prix n'ont pas été trouvés

**Colonnes requises dans le fichier Excel :**
- `Set #` : Numéro de carte (ex: "001/191")
- `Name` : Nom de la carte (ex: "Pikachu")
- `Set` : Nom du set (optionnel, aide à filtrer)

**Colonnes ajoutées :**
- `Prix` : Prix market par défaut (format normal ou holofoil)
- `Prix max` : Prix market maximum (tous formats confondus)

#### 🔍 Recherche Rapide de Carte
Recherche instantanée d'une carte :
- **Nom** : Nom de la carte (requis)
- **Numéro** : Numéro de carte (optionnel, ex: "057")
- **Set** : Nom du set (optionnel, aide à filtrer)
- **Résultat** : Popup avec tous les prix disponibles par format

**Exemple de résultat :**
```
Carte: Pikachu ex
Numéro: 057
Set: Surging Sparks

Prix TCGPlayer:
  normal: $4.50
  holofoil: $8.25
  reverse holofoil: $6.00
```

**💡 Clé API incluse** - Prête à l'emploi, aucune configuration nécessaire!

### �📝 Onglet Logs

**Fonctionnalités :**
- 📋 **Copier** : Copier les logs dans le presse-papier
- 💾 **Sauvegarder** : Exporter les logs en fichier .log
- 🗑️ **Effacer** : Nettoyer la zone de logs
- ⏰ Horodatage automatique de chaque message

### 🔄 Barre de Progression

- ⏳ Indicateur visuel pendant les opérations
- 🛑 Bouton Annuler pour interrompre
- 📊 Affichage du statut en temps réel
- ✅ L'interface ne se fige plus pendant les traitements !

### 📁 Menu Fichier

- Ouvrir dossier Images
- Ouvrir dossier Output
- Quitter

### 🛠️ Menu Outils

- **Nettoyer Output** : Supprime tous les fichiers de sortie
- **Diagnostiquer Environnement** : Vérifie Python, dépendances, dossiers
- **Réinstaller Dépendances** : Réinstalle requirements.txt

### ❓ Menu Aide

- **Guide d'utilisation** : Ouvre GUIDE_UTILISATION.md
- **À propos** : Informations sur la version

## 🔥 Workflow Recommandé

### Workflow Classique

1. **Préparer les images sources**
   - Placer vos cartes Pokemon dans le dossier `Images Sources`
   - Créer le fichier `cards_info.xlsx` avec les informations

2. **Générer les fausses cartes** (Onglet Fausses Cartes)
   - Choisir le nombre de cartes (ex: 20)
   - Activer Random Erasing
   - Régler la probabilité (ex: 0.8)
   - Cliquer **▶️ Générer**

3. **Augmentation** (Onglet Augmentation)
   - Choisir le nombre d'augmentations (ex: 15)
   - Sélectionner la cible (augmented)
   - Cliquer **▶️ Lancer l'Augmentation**

4. **Générer les mosaïques** (Onglet Mosaïques)
   - Configurer les modes souhaités
   - Cliquer **▶️ Générer les Mosaïques**

### Workflow Automatique

**Dashboard → ▶️ Démarrer Workflow**

Exécute automatiquement :
1. Génération fausses cartes
2. Augmentation (15 images)
3. Mosaïques (layout=1, bg=0, transform=0)

## 💾 Configuration Persistante

Tous vos réglages sont sauvegardés dans `gui_config.json` :
```json
{
    "paths": {
        "images_source": "images",
        "fakeimg": "fakeimg",
        "output_augmented": "output\\augmented",
        "output_mosaic": "output\\yolov8",
        "excel_file": "cards_info.xlsx"
    },
    "last_used": {
        "num_aug": 15,
        "target": "augmented",
        "layout_mode": 1,
        "background_mode": 0,
        "transform_mode": 0,
        "random_erasing_p": 0.2
    }
}
```

## 🐛 Dépannage

### Le GUI ne démarre pas
```batch
# Vérifier l'environnement
.\.venv\Scripts\python.exe --version

# Réinstaller les dépendances
.\install_env.bat
```

### Erreur "ModuleNotFoundError"
```batch
# Activer l'environnement et installer manuellement
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Diagnostic complet
Dans le GUI : Menu `Outils` → `Diagnostiquer Environnement`

## 📦 Dépendances Principales

- Python 3.12
- NumPy < 2.0 (compatibilité imgaug)
- OpenCV < 4.10.0 (compatibilité NumPy 1.x)
- imgaug 0.4.0
- pandas
- pillow
- scikit-image

## 🆚 Différences v1 vs v2

| Fonctionnalité | v1 (GUI.py) | v2 (GUI_v2.py) |
|----------------|-------------|----------------|
| Configuration chemins | ❌ Hardcodé | ✅ Menu Settings |
| Validation | ❌ Non | ✅ Automatique |
| Barre de progression | ❌ Non | ✅ Oui |
| Threading | ❌ Interface fige | ✅ Multi-thread |
| Fausses cartes | ❌ Batch séparé | ✅ Intégré |
| Dashboard | ❌ Non | ✅ Oui |
| Logs avancés | ❌ Basique | ✅ Export, copie |
| Presets | ❌ Non | ✅ Rapide/Standard/Intensif |
| Config persistante | ❌ Non | ✅ gui_config.json |

## 📞 Support

Pour toute question, consulter :
- `GUIDE_UTILISATION.md` : Guide complet
- `CHANGELOG_MODIFICATIONS.md` : Liste des modifications
- Menu Aide → Guide d'utilisation

---

**Version 2.0** - Octobre 2025
© Pokemon Dataset Generator
