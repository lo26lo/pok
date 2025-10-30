# 📝 CHANGELOG - GUI v2.0

## 🎉 Version 2.0.1 - Octobre 2025

### ✨ Nouvelles Fonctionnalités

#### 🔧 Onglet Utilitaires - API Pokémon TCG (Nouveau !)
- **Intégration complète de l'API Pokémon TCG** avec clé API incluse
- **3 outils puissants** pour gérer vos collections :

##### 📋 Générer Liste de Cartes
  - Récupère automatiquement toutes les cartes d'une extension depuis l'API
  - Génère un fichier Excel avec colonnes `Set #` (001/191) et `Name`
  - Gestion de la pagination (traite des centaines de cartes automatiquement)
  - Exemple : "Surging Sparks" → 191 cartes en quelques secondes
  - Idéal pour démarrer une nouvelle collection

##### 💰 Mise à Jour des Prix
  - Lit un fichier Excel avec `Set #`, `Name`, `Set`
  - Interroge l'API TCGPlayer pour chaque carte (parallélisé, max 5 workers)
  - Ajoute colonnes `Prix` (market par défaut) et `Prix max` (tous formats)
  - Affiche progression en temps réel dans les logs
  - Résumé final avec nombre de succès/erreurs
  - Filtrage intelligent par numéro et set pour trouver la bonne carte

##### 🔍 Recherche Rapide
  - Recherche instantanée d'une carte par nom
  - Filtres optionnels : numéro de carte et nom du set
  - Affiche popup avec tous les prix disponibles par format (normal, holofoil, reverse, etc.)
  - Parfait pour vérifier rapidement la valeur d'une carte

**Fonctionnalités techniques :**
- Exécution en thread séparé (interface non-bloquante)
- Gestion d'erreurs robuste avec logs détaillés
- API key intégrée (d71261e0-202c-41a6-93a9-fdcb3a7f9790)
- Support complet des formats TCGPlayer

---

## 🎉 Version 2.0 - Octobre 2025

### ✨ Nouvelles Fonctionnalités Majeures

#### 🔧 Menu Settings - Configuration Personnalisable
- **Nouveau menu complet** permettant de personnaliser tous les chemins du projet
- Interface graphique avec boutons de navigation pour choisir facilement les dossiers
- Sauvegarde automatique dans `gui_config.json`
- Bouton de réinitialisation aux valeurs par défaut
- Chemins configurables :
  - Dossier Images Sources
  - Dossier Fausses Cartes (fakeimg)
  - Sortie Augmentation
  - Sortie Mosaïques
  - Fichier Excel

#### 📊 Onglet Dashboard
- **Nouveau** : Vue d'ensemble avec statistiques en temps réel
- Compteurs automatiques pour :
  - Images sources disponibles
  - Fausses cartes générées
  - Images augmentées
  - Mosaïques créées
- Actions rapides intégrées :
  - Ouvrir dossiers Images, Output, Excel
  - Nettoyer les dossiers de sortie
  - Diagnostiquer l'environnement
- **Workflow Complet** : Bouton pour automatiser tout le processus (fakeimg + augmentation + mosaïques)

#### 🖼️ Onglet Fausses Cartes (Nouveau !)
- **Plus besoin de batch file séparé !**
- Interface complète pour gérer les fausses cartes :
  - Slider pour le nombre de cartes (10-50)
  - Checkbox pour activer/désactiver Random Erasing
  - Slider pour la probabilité d'effacement (0.0-1.0)
- Génération automatique :
  1. Copie aléatoire depuis Images Sources
  2. Application du Random Erasing si activé
  3. Sortie dans fakeimg_augmented

#### ✅ Validation Automatique
- **Onglet Augmentation** : Vérifie l'existence des images sources et du fichier Excel
- **Onglet Mosaïques** : Vérifie les images augmentées et les fausses cartes
- Messages clairs indiquant :
  - ✅ Ce qui est prêt (avec compteurs)
  - ❌ Ce qui manque
  - ⚠️ Les avertissements

#### ⏳ Barre de Progression
- Indicateur visuel animé pendant les opérations
- Label dynamique affichant l'opération en cours
- Bouton **Annuler** pour interrompre les processus
- Statut global dans l'en-tête (✅ Prêt / ⏳ En cours)

#### 🧵 Multi-threading
- **Interface ne fige plus** pendant les opérations longues
- Exécution asynchrone des processus Python
- Logs en temps réel pendant l'exécution
- Possibilité d'annuler les opérations en cours

#### 📝 Logs Améliorés
- Horodatage automatique de chaque message
- Boutons d'action :
  - 📋 Copier dans le presse-papier
  - 💾 Sauvegarder en fichier .log avec timestamp
  - 🗑️ Effacer les logs
- Zone de texte scrollable avec formatage amélioré

#### ⚡ Presets Rapides
- **Onglet Augmentation** : Boutons presets
  - Rapide (5 augmentations)
  - Standard (15 augmentations)
  - Intensif (100 augmentations)
- Application en un clic

#### 💾 Configuration Persistante
- Sauvegarde automatique de tous les réglages dans `gui_config.json`
- Mémorisation entre les sessions :
  - Tous les chemins personnalisés
  - Dernier nombre d'augmentations utilisé
  - Dernière cible sélectionnée
  - Derniers modes de mosaïque (layout, background, transform)
  - Dernière probabilité Random Erasing
- Chargement automatique au démarrage

### 🎨 Améliorations de l'Interface

#### Structure Modernisée
- **5 onglets** au lieu de 4 :
  1. 📊 Dashboard (nouveau)
  2. 🎨 Augmentation
  3. 🧩 Mosaïques
  4. 🖼️ Fausses Cartes (nouveau)
  5. 📝 Logs
- En-tête avec titre et statut global
- Barre de progression en pied de page

#### Menu Enrichi
- **Menu Fichier** :
  - Ouvrir dossier Images
  - Ouvrir dossier Output
  - Quitter
- **Menu Outils** :
  - Nettoyer Output
  - Diagnostiquer Environnement
  - Réinstaller Dépendances
- **Menu Settings** (nouveau) :
  - Chemins et Configuration
- **Menu Aide** :
  - Guide d'utilisation
  - À propos

#### Icônes et Emojis
- Utilisation d'icônes pour meilleure lisibilité
- Emojis dans les titres d'onglets
- Indicateurs visuels (✅, ❌, ⚠️, ⏳)

### 🔧 Améliorations Techniques

#### Gestion des Erreurs
- Try-catch sur toutes les opérations critiques
- Messages d'erreur clairs avec suggestions
- Logging détaillé de toutes les exceptions

#### Gestion des Chemins
- Support des chemins absolus et relatifs
- Création automatique des dossiers manquants
- Validation des chemins avant exécution

#### Gestion des Processus
- Utilisation de `subprocess.Popen` pour contrôle fin
- Capture stdout/stderr en temps réel
- Vérification des codes retour
- Nettoyage des processus zombies

#### Documentation Intégrée
- Tooltips (à venir)
- Messages d'aide contextuels
- Fenêtre "À propos" avec version et fonctionnalités

### 🐛 Corrections de Bugs

#### v1 → v2
- **Résolu** : Interface qui fige pendant les opérations longues
- **Résolu** : Impossibilité de changer les chemins des dossiers
- **Résolu** : Pas de validation avant lancement
- **Résolu** : Nécessité d'utiliser des batch séparés pour fakeimg
- **Résolu** : Paramètres non mémorisés entre sessions
- **Résolu** : Pas de feedback pendant l'exécution
- **Résolu** : Impossibilité d'annuler une opération

### 📦 Fichiers Créés/Modifiés

#### Nouveaux Fichiers
- `GUI_v2.py` : Interface modernisée
- `run_gui_v2_with_env.bat` : Lanceur pour environnement virtuel
- `gui_config.json` : Configuration persistante (auto-généré)
- `README_GUI_V2.md` : Documentation complète
- `CHANGELOG_GUI_V2.md` : Ce fichier

#### Fichiers Modifiés
- `requirements.txt` : Simplifié, versions conflictuelles supprimées

#### Fichiers Conservés
- `GUI.py` : Version originale conservée pour compatibilité
- `01_run_with_env.bat` : Lance GUI.py v1
- Tous les scripts Python de traitement (augmentation.py, mosaic.py, etc.)

### 🔄 Migration v1 → v2

#### Compatibilité
- ✅ **100% rétrocompatible** : v1 continue de fonctionner
- ✅ Utilise les mêmes scripts Python (augmentation.py, mosaic.py)
- ✅ Même structure de dossiers
- ✅ Même format Excel

#### Différences de Lancement
```batch
# v1
01_run_with_env.bat

# v2
run_gui_v2_with_env.bat
```

#### Configuration par Défaut
Au premier lancement de v2, la configuration par défaut est créée avec les mêmes chemins que v1.

### 🎯 Cas d'Usage Améliorés

#### Avant (v1)
```
1. Éditer les scripts pour changer les chemins
2. Lancer generate_fakeimages.bat séparément
3. Lancer GUI.py
4. Attendre sans feedback visuel
5. Vérifier manuellement si terminé
```

#### Après (v2)
```
1. Lancer GUI v2
2. (Optionnel) Configurer les chemins dans Settings
3. Dashboard → tout voir d'un coup d'œil
4. Onglet Fausses Cartes → générer en quelques clics
5. Barre de progression + logs en temps réel
6. Configuration mémorisée pour la prochaine fois
```

### 📊 Statistiques

#### Lignes de Code
- GUI v1 : ~400 lignes
- GUI v2 : ~900 lignes (+ 125% de fonctionnalités)

#### Fonctionnalités
- GUI v1 : 8 fonctionnalités de base
- GUI v2 : 25+ fonctionnalités

#### Onglets
- GUI v1 : 4 onglets
- GUI v2 : 5 onglets

### 🚀 Améliorations Futures (Roadmap)

#### Version 2.1 (Potentielle)
- [ ] Thème sombre/clair sélectionnable
- [ ] Tooltips sur tous les contrôles
- [ ] Prévisualisation des images
- [ ] Historique des opérations
- [ ] Export des statistiques en CSV
- [ ] Mode batch avancé
- [ ] Profils de configuration multiples
- [ ] Gestion des favoris

#### Version 2.2 (Potentielle)
- [ ] Graphique de progression détaillé
- [ ] Comparaison avant/après
- [ ] Galerie d'images générées
- [ ] Planificateur de tâches
- [ ] Notifications système
- [ ] Multi-langue (FR/EN)

### 🎓 Remerciements

Développement basé sur les retours utilisateurs et l'analyse des workflows réels d'utilisation.

---

**Version 2.0** - Octobre 2025
**Auteur** : GitHub Copilot
**Licence** : Même licence que le projet principal
