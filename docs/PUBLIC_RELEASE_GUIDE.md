# 📦 Script de Publication Publique

Ce script permet de créer un repository GitHub **public** avec un seul commit initial, **sans exposer l'historique de développement**.

---

## 🎯 Objectif

Publier le code source du projet de manière propre et professionnelle, sans révéler :
- ❌ L'historique complet des commits
- ❌ Les commits de travail en cours (WIP)
- ❌ Les erreurs et corrections intermédiaires
- ❌ Les données de développement

Tout en conservant :
- ✅ Le code source complet et fonctionnel
- ✅ Toute la documentation
- ✅ Les scripts et tests
- ✅ La configuration du projet

---

## 🚀 Utilisation

### Méthode 1 : Via le fichier .bat (Plus simple)

```batch
cd C:\DATA\pok
scripts\create_public_release.bat https://github.com/votre-compte/nom-du-repo.git
```

Avec une version spécifique :
```batch
scripts\create_public_release.bat https://github.com/votre-compte/nom-du-repo.git v3.3
```

### Méthode 2 : Via PowerShell directement

```powershell
cd C:\DATA\pok
.\scripts\create_public_release.ps1 -RepoUrl "https://github.com/votre-compte/nom-du-repo.git"
```

Avec paramètres optionnels :
```powershell
.\scripts\create_public_release.ps1 `
    -RepoUrl "https://github.com/votre-compte/nom-du-repo.git" `
    -Version "v3.3" `
    -TempDir "C:\TEMP\pok-release"
```

---

## 📋 Pré-requis

1. **Créer le repository sur GitHub** :
   - Aller sur https://github.com/new
   - Créer un repository **vide** (ne pas initialiser avec README, .gitignore, ou license)
   - Choisir la visibilité : **Public**
   - Noter l'URL : `https://github.com/votre-compte/nom-du-repo.git`

2. **Être dans le dossier du projet** :
   ```batch
   cd C:\DATA\pok
   ```

3. **Avoir Git installé et configuré**

---

## 🔧 Ce que fait le script

### Étape 1 : Préparation
- Crée un dossier temporaire
- Copie tous les fichiers du projet

### Étape 2 : Exclusions automatiques
Le script exclut automatiquement :
- **Dossiers** : `.git`, `.venv`, `__pycache__`, `.vscode`, `output`, `images`, `runs`, `.planning`
- **Fichiers** : `*.log`, `*.pyc`

### Étape 3 : Initialisation Git
- Initialise un nouveau repository Git (sans historique)
- Ajoute tous les fichiers

### Étape 4 : Commit unique
Crée un seul commit avec une description complète :
```
Initial release - Pokemon Dataset Generator v3.2

Complete YOLO pipeline for Pokemon card detection with modern GUI:
- Dataset generation with 22+ augmentation techniques
- Holographic effects (5+ styles)
- Ultra-fast mosaic generation (30-60x faster)
- One-click YOLOv8/v11 training
- Live detection with real-time price integration
...
```

### Étape 5 : Publication
- Configure le remote vers votre nouveau repository
- Pousse le code sur GitHub
- **Résultat** : 1 seul commit visible sur GitHub

### Étape 6 : Nettoyage
- Supprime le dossier temporaire
- Affiche un résumé

---

## 📊 Exemple de sortie

```
================================================================
  Script de Publication Publique - Pokemon Dataset Generator
================================================================

✓ Dossier du projet: C:\DATA\pok
✓ Repository cible: https://github.com/lo26lo/Pokemon-Dataset-Creator.git
✓ Version: v3.2

[1/7] Création du dossier temporaire...
   ✓ Dossier créé: C:\DATA\pok-public-temp

[2/7] Copie des fichiers du projet...
   Exclusions:
   - Dossiers: .git, .venv, __pycache__, .vscode, output, images, runs, .planning
   - Fichiers: *.log, *.pyc
   ✓ Fichiers copiés avec succès

[3/7] Initialisation du repository Git...
   ✓ Repository Git initialisé

[4/7] Ajout des fichiers au staging...
   ✓ 421 fichiers ajoutés

[5/7] Création du commit initial...
   ✓ Commit créé: Initial release v3.2

[6/7] Configuration du remote et push...
   Push vers https://github.com/lo26lo/Pokemon-Dataset-Creator.git...
   ✓ Code publié avec succès !

[7/7] Nettoyage du dossier temporaire...
   ✓ Dossier temporaire supprimé

================================================================
✅ PUBLICATION RÉUSSIE !
================================================================

📦 Repository public:
   https://github.com/lo26lo/Pokemon-Dataset-Creator.git

📊 Statistiques:
   - 1 commit unique
   - 421 fichiers
   - Version: v3.2

🔒 Repository privé:
   - Historique complet conservé
   - Tous les commits préservés

💡 Prochaines étapes recommandées:
   1. Vérifier le repository sur GitHub
   2. Ajouter une LICENSE (ex: MIT)
   3. Créer une release GitHub
   4. Configurer les settings du repository
```

---

## ⚙️ Paramètres

| Paramètre | Description | Requis | Défaut | Exemple |
|-----------|-------------|--------|--------|---------|
| `-RepoUrl` | URL du repository GitHub cible | ✅ Oui | - | `https://github.com/user/repo.git` |
| `-Version` | Numéro de version du release | ❌ Non | `v3.2` | `v3.3`, `v4.0` |
| `-TempDir` | Dossier temporaire pour la préparation | ❌ Non | `C:\DATA\pok-public-temp` | `C:\TEMP\release` |

---

## 🔒 Sécurité

### Ce qui est publié
✅ Code source complet  
✅ Documentation  
✅ Scripts utilitaires  
✅ Tests  
✅ Configuration (requirements, .gitignore, etc.)  

### Ce qui N'est PAS publié
❌ Historique de développement (commits)  
❌ Environnement virtuel (.venv)  
❌ Données générées (output/, images/, runs/)  
❌ Fichiers de cache (__pycache__, *.pyc)  
❌ Configuration IDE (.vscode/)  
❌ Fichiers de logs  
❌ Documents de planification (.planning/)  

---

## 💡 Cas d'usage

### 1. Première publication
```batch
REM Créer le repo sur GitHub, puis :
scripts\create_public_release.bat https://github.com/user/pokemon-dataset.git v1.0
```

### 2. Mise à jour majeure
```batch
REM Le repository existe déjà, vous pouvez le supprimer et recréer, ou :
REM 1. Supprimer l'ancien repo sur GitHub
REM 2. Recréer un repo vide
REM 3. Relancer le script
scripts\create_public_release.bat https://github.com/user/pokemon-dataset.git v2.0
```

### 3. Test avant publication
```batch
REM Utiliser un repository de test
scripts\create_public_release.bat https://github.com/user/test-release.git test
```

---

## ⚠️ Avertissements

1. **Le repository cible doit être vide** : Le script effectue un push initial. Si le repository contient déjà des commits, le push échouera.

2. **Vérifier les exclusions** : Assurez-vous que les dossiers exclus ne contiennent pas de fichiers essentiels au projet.

3. **Tester d'abord** : Créez un repository de test pour vérifier que tout fonctionne avant de publier officiellement.

4. **Pas de retour en arrière** : Une fois publié, le code est public. Assurez-vous de ne pas avoir inclus de données sensibles.

---

## 🐛 Dépannage

### Erreur : "Ce script doit être exécuté depuis la racine du projet"
**Solution** : Assurez-vous d'être dans `C:\DATA\pok` avant de lancer le script.

### Erreur : "Erreur lors du push"
**Causes possibles** :
- Le repository cible n'existe pas
- Le repository cible n'est pas vide
- Problème d'authentification Git
- Pas de connexion internet

**Solution** : Vérifiez que le repository existe et est vide sur GitHub.

### Le script s'arrête pendant la copie
**Solution** : Vérifiez que vous avez les droits d'écriture sur le dossier temporaire.

---

## 📚 Références

- Script PowerShell : `scripts/create_public_release.ps1`
- Script Batch : `scripts/create_public_release.bat`
- Catalogue : `scripts/SCRIPTS_REFERENCE.py` (section Publishing)

---

**Dernière mise à jour** : 14 novembre 2025  
**Version du script** : 1.0
