# 🌍 Intégration TCGdex API

## 📋 Table des Matières
- [Vue d'ensemble](#-vue-densemble)
- [Pourquoi TCGdex ?](#-pourquoi-tcgdex-)
- [Configuration](#-configuration)
- [Fonctionnalités](#-fonctionnalités)
- [Exemples d'utilisation](#-exemples-dutilisation)
- [API Reference](#-api-reference)
- [Langues supportées](#-langues-supportées)
- [Dépannage](#-dépannage)

---

## 🌟 Vue d'ensemble

**TCGdex** est une API communautaire **gratuite et open-source** qui agrège les données de cartes Pokémon depuis plusieurs sources, incluant **Cardmarket** (Europe) et **TCGPlayer** (USA).

### ⭐ Avantages Clés

| Fonctionnalité | TCGdex | Pokemon TCG API | Cardmarket API |
|----------------|--------|-----------------|----------------|
| **Authentification** | ❌ Aucune | ✅ Clé API | ✅ OAuth 1.0 |
| **Configuration** | 🟢 1 min | 🟡 5 min | 🔴 15+ min |
| **Vitesse** | ⚡ Ultra-rapide | 🐌 Moyen | 🐌 Lent |
| **Prix Cardmarket** | ✅ Oui (EUR) | ❌ Non | ✅ Oui (EUR) |
| **Prix TCGPlayer** | ✅ Oui (USD) | ✅ Oui (USD) | ❌ Non |
| **Multilingue** | ✅ 10+ langues | ✅ Anglais | ✅ Multilingue |
| **Rate Limits** | 🟢 Permissif | 🟡 Modéré | 🔴 Strict |
| **Coût** | 💰 GRATUIT | 💰 GRATUIT | 💰 GRATUIT |

**🎯 Recommandation** : TCGdex est **l'option idéale** pour démarrer rapidement sans configuration.

---

## 💡 Pourquoi TCGdex ?

### 1️⃣ Aucune Configuration Requise
```json
{
    "api_source": "tcgdex",
    "tcgdex": {
        "language": "en"
    }
}
```
**C'est tout !** Pas de clé API, pas d'OAuth, pas de tokens.

### 2️⃣ Meilleur des Deux Mondes
TCGdex combine automatiquement :
- 🇪🇺 **Cardmarket** : Prix tendance européens (EUR)
- 🇺🇸 **TCGPlayer** : Prix marché américains (USD)

### 3️⃣ Ultra-Rapide
- **Génération de liste** : 1 requête au lieu de ~10 (pagination)
- **Mise à jour prix** : 0.3s/carte vs 1s/carte
- **252 cartes Surging Sparks** : ~76s au lieu de 4+ minutes

### 4️⃣ Multilingue
Supporté : `en`, `fr`, `es`, `it`, `pt`, `de`, `ja`, `zh`, `id`, `th`

---

## ⚙️ Configuration

### Méthode 1 : Interface Graphique (Recommandé)

1. **Lancer le GUI** : `run_gui_v2_with_env.bat`
2. **Menu → Configuration API**
3. **Sélectionner "TCGdex"** (première option)
4. **Choisir la langue** (ex : Français)
5. **Tester la connexion** → Doit afficher "Connexion réussie !"
6. **Sauvegarder**

### Méthode 2 : Fichier JSON Manuel

Éditer `api_config.json` :

```json
{
    "api_source": "tcgdex",
    "tcgdex": {
        "language": "fr"
    }
}
```

**Langues disponibles** : `en`, `fr`, `es`, `it`, `pt`, `de`, `ja`, `zh`, `id`, `th`

---

## 🎯 Fonctionnalités

### 1️⃣ Génération de Liste de Cartes

**Interface GUI** : Onglet `🔧 Utilitaires` → `📋 Générer Liste de Cartes`

**Entrée** :
- Nom du set : `Surging Sparks`
- OU ID du set : `sv08`

**Sortie** : Fichier Excel avec colonnes :
- `Set #` : `001/191`, `002/191`, ...
- `Name` : `Exeggcute`, `Exeggcute`, ...
- `Set` : `Surging Sparks`

**Avantages vs autres APIs** :
- ⚡ **1 seule requête** au lieu de pagination
- 🚀 **2-3 secondes** vs 1-2 minutes
- 📊 **Toutes les cartes** du set en une fois

**Sets mappés automatiquement** :
```python
'surging sparks' → 'sv08'
'stellar crown' → 'sv07'
'shrouded fable' → 'sv06'
'twilight masquerade' → 'sv05'
'temporal forces' → 'sv04'
'paldean fates' → 'sv03'
'paradox rift' → 'sv02'
'obsidian flames' → 'sv01'
'151' → 'sv151'
'base set' → 'base1'
# ... et plus
```

### 2️⃣ Mise à Jour des Prix

**Interface GUI** : Onglet `🔧 Utilitaires` → `💰 Mettre à Jour les Prix`

**Entrée** : Fichier Excel avec colonnes :
- `Set #` : `001/191`
- `Name` : `Exeggcute`
- `Set` : `Surging Sparks`

**Sortie** : Fichier Excel enrichi avec :
- `Prix` : Prix minimum (trend CM ou marketPrice TCP)
- `Prix max` : Prix maximum (variants)
- `SourcePrix` : `TCGdex(Cardmarket)` ou `TCGdex(TCGPlayer)`

**Priorité des prix** :
1. **Cardmarket trend** (prix tendance EUR)
2. **TCGPlayer marketPrice** (prix marché USD)
3. Autres prix disponibles

**Performance** :
- 252 cartes : ~76 secondes (0.3s/carte)
- Parallélisation : 1 worker (séquentiel pour éviter surcharge)
- Logs en temps réel : progression toutes les 10 cartes ou 5s

### 3️⃣ Recherche Rapide

**Interface GUI** : Onglet `🔧 Utilitaires` → `🔍 Recherche Rapide`

**Exemple** :
- Nom : `Charizard`
- Set : `Base Set`
- Numéro : `4`

**Résultat** : Popup avec tous les prix disponibles

---

## 📚 API Reference

### Module `tcgdex_api.py`

#### Classe `TCGdexAPI`

```python
from tcgdex_api import TCGdexAPI

# Initialiser
api = TCGdexAPI(language='fr')

# Rechercher des cartes
cards = api.search_cards('Pikachu', set_name='Base Set')

# Obtenir une carte spécifique
card = api.get_card('base1-004')  # Charizard Base Set

# Extraire les prix
price_avg, price_max, source = api.extract_prices(card)

# Tout-en-un
price, pmax, details = api.search_card_with_prices(
    card_name='Pikachu',
    set_name='Surging Sparks',
    card_number='025/191'
)
```

#### Méthodes Principales

##### `__init__(language='en')`
Initialise le client TCGdex.

**Paramètres** :
- `language` : Code langue (en, fr, es, it, pt, de, ja, zh, id, th)

##### `search_cards(card_name, set_name=None)`
Recherche des cartes par nom.

**Retour** : Liste de cartes (format simplifié)

##### `get_card(card_id)`
Récupère les détails complets d'une carte avec pricing.

**Retour** : Dict avec pricing Cardmarket + TCGPlayer

##### `extract_prices(card)`
Extrait les prix d'une carte.

**Retour** : `(price_avg, price_max, source)`
- `price_avg` : Prix minimum (float)
- `price_max` : Prix maximum (float)
- `source` : `"TCGdex(Cardmarket)"` ou `"TCGdex(TCGPlayer)"`

##### `search_card_with_prices(card_name, set_name=None, card_number=None)`
Recherche tout-en-un avec stratégie optimisée.

**Stratégie 1** : Si set mappé + numéro fourni → construction directe ID
**Stratégie 2** : Recherche classique par nom (fallback)

**Retour** : `(price_avg, price_max, card_details)`

---

## 🌍 Langues Supportées

| Code | Langue | Exemple |
|------|--------|---------|
| `en` | English | Pikachu |
| `fr` | Français | Pikachu |
| `es` | Español | Pikachu |
| `it` | Italiano | Pikachu |
| `pt` | Português | Pikachu |
| `de` | Deutsch | Pikachu |
| `ja` | 日本語 | ピカチュウ |
| `zh` | 中文 | 皮卡丘 |
| `id` | Indonesia | Pikachu |
| `th` | ไทย | พิคาชู |

**Note** : Les prix restent en EUR (Cardmarket) ou USD (TCGPlayer) quelle que soit la langue.

---

## 🔧 Dépannage

### ❌ Erreur : "Set 'Surging Sparks' non trouvé"

**Solution** : Utilisez l'ID du set au lieu du nom
```
"Surging Sparks" → "sv08"
"Stellar Crown" → "sv07"
```

### ⚠️ Prix trouvés : 0/252

**Causes possibles** :
1. **Set très récent** : Pas encore de prix sur TCGdex
2. **Nom de set incorrect** : Vérifier l'orthographe
3. **Cartes promos** : Peuvent ne pas avoir de prix

**Solution** : Vérifier manuellement une carte sur https://www.tcgdex.net/

### 🐌 API lente

**TCGdex ne devrait jamais être lent.** Si c'est le cas :
1. Vérifier votre connexion internet
2. Essayer avec un autre set
3. L'API TCGdex peut être temporairement surchargée

### 🔄 Erreur 404

**Carte non trouvée** : Vérifier que :
1. Le nom de la carte est correct
2. Le set existe sur TCGdex
3. Le numéro de carte est exact

---

## 📊 Exemples Concrets

### Exemple 1 : Générer Surging Sparks

**GUI** :
1. Onglet Utilitaires
2. Nom : `sv08` (ou `Surging Sparks`)
3. Fichier : `surging_sparks.xlsx`
4. Cliquer "Générer Excel"

**Résultat** : ~2 secondes, 252 cartes

### Exemple 2 : Mettre à jour les prix

**GUI** :
1. Générer la liste (voir Exemple 1)
2. Onglet Utilitaires → Mise à jour prix
3. Fichier entrée : `surging_sparks.xlsx`
4. Fichier sortie : `surging_sparks_prices.xlsx`
5. Cliquer "Mettre à Jour les Prix"

**Résultat** : ~76 secondes, prix Cardmarket + TCGPlayer

### Exemple 3 : Recherche Charizard

**GUI** :
1. Onglet Utilitaires → Recherche Rapide
2. Nom : `Charizard`
3. Set : `Base Set`
4. Numéro : `4`
5. Cliquer "Rechercher Prix"

**Résultat** : Popup avec prix EUR + USD

---

## 🔗 Ressources

- **Site officiel** : https://www.tcgdex.net/
- **Documentation API** : https://api.tcgdex.net/v2/en/
- **GitHub** : https://github.com/tcgdex
- **Discord** : Community support

---

## 📝 Notes Importantes

### ⚡ Performance
- **Génération liste** : 100x plus rapide que Pokemon TCG API
- **Mise à jour prix** : 3x plus rapide que Cardmarket API
- **Pas de rate limit strict** : Peut traiter des milliers de cartes

### 💰 Prix
- **Cardmarket** : EUR, mis à jour quotidiennement
- **TCGPlayer** : USD, mis à jour horaire
- **Source affichée** : Indique quelle API a fourni le prix

### 🌍 Open Source
- API communautaire maintenue par des passionnés
- Code source disponible sur GitHub
- Contributions bienvenues

---

## ✅ Checklist de Démarrage

- [ ] GUI lancé : `run_gui_v2_with_env.bat`
- [ ] Menu → Configuration API
- [ ] TCGdex sélectionné (première option)
- [ ] Langue choisie (ex : Français)
- [ ] Test connexion réussi
- [ ] Configuration sauvegardée
- [ ] Première liste générée
- [ ] Prix mis à jour avec succès

**🎉 Félicitations ! Vous êtes prêt à utiliser TCGdex !**

---

*Dernière mise à jour : Octobre 2025*
