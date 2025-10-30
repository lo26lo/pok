# Configuration de la clé API Pokémon TCG

## 🔑 Configuration initiale

1. Copiez le fichier exemple :
   ```bash
   copy api_config.json.example api_config.json
   ```

2. Ouvrez `api_config.json` et remplacez `YOUR_API_KEY_HERE` par votre clé API Pokémon TCG

3. Obtenez votre clé API gratuite sur : https://pokemontcg.io/

## ⚠️ Sécurité

- ❌ **NE JAMAIS** commiter le fichier `api_config.json` sur Git
- ✅ Le fichier est déjà dans `.gitignore`
- ✅ Utilisez `api_config.json.example` comme template
- ✅ Chaque développeur doit créer son propre `api_config.json`

## 📝 Format du fichier

```json
{
    "pokemon_tcg_api_key": "votre-clé-api-ici"
}
```

## 🔧 Fonctionnalités nécessitant la clé API

- Génération de liste d'extensions depuis l'API
- Mise à jour des prix des cartes
- Recherche de cartes individuelles
