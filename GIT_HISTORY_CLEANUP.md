# 🔐 Nettoyage de l'historique Git - Suppression de la clé API

## ⚠️ IMPORTANT : Révoquez d'abord votre ancienne clé API !

Avant de nettoyer l'historique, **créez une nouvelle clé API** sur https://pokemontcg.io/ et **révoquez l'ancienne**.

## 🧹 Méthode recommandée : BFG Repo-Cleaner

### Installation
1. Téléchargez BFG : https://rtyley.github.io/bfg-repo-cleaner/
2. Placez `bfg.jar` dans un dossier accessible

### Nettoyage

```bash
# 1. Créer un fichier avec la clé à supprimer
echo "d71261e0-202c-41a6-93a9-fdcb3a7f9790" > api-key-to-remove.txt

# 2. Cloner le repo en mirror
cd ..
git clone --mirror https://github.com/lo26lo/pok.git pok-clean.git

# 3. Nettoyer avec BFG
java -jar bfg.jar --replace-text api-key-to-remove.txt pok-clean.git

# 4. Nettoyer et comprimer
cd pok-clean.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (⚠️ ATTENTION : ceci réécrit l'historique)
git push --force

# 6. Supprimer le clone mirror
cd ..
rm -rf pok-clean.git
```

## 📝 Alternative : Réécriture manuelle avec git-filter-repo

```bash
# Installer git-filter-repo
pip install git-filter-repo

# Nettoyer
git filter-repo --invert-paths --path GUI_v2.py --force
```

## ⚠️ Après le nettoyage

1. **Tous les collaborateurs** doivent re-cloner le repo :
   ```bash
   git clone https://github.com/lo26lo/pok.git
   ```

2. Ne pas faire de `git pull` sur les anciens clones (l'historique a changé)

3. Vérifier que la clé n'apparaît plus :
   ```bash
   git log --all --source --full-history -S "d71261e0-202c-41a6-93a9-fdcb3a7f9790"
   ```

## 🔒 Prévention future

- ✅ La clé est maintenant dans `api_config.json` (gitignored)
- ✅ Utilisez des outils comme `git-secrets` pour détecter les secrets
- ✅ Activez GitHub Secret Scanning dans les paramètres du repo

## 📚 Ressources

- BFG Repo-Cleaner : https://rtyley.github.io/bfg-repo-cleaner/
- GitHub : Removing sensitive data : https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository
- git-filter-repo : https://github.com/newren/git-filter-repo
