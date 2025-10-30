# 📦 Création d'un Executable Windows (.exe)

## 🎯 Objectif

Créer une version **portable** et **standalone** du Pokemon Dataset Generator qui peut être distribuée et utilisée **sans installer Python**.

---

## ⚡ Utilisation Rapide

### Méthode 1 : Script Automatique (Recommandé)

```batch
# Double-cliquez sur :
create_exe.bat
```

Le script va :
1. ✅ Vérifier l'environnement virtuel
2. ✅ Installer PyInstaller (si nécessaire)
3. ✅ Nettoyer les builds précédents
4. ✅ Créer l'executable (5-10 minutes)
5. ✅ Créer un package portable complet

### Méthode 2 : Manuel

```batch
# Activer l'environnement
.venv\Scripts\activate

# Installer PyInstaller
pip install pyinstaller

# Créer l'exe
python create_exe.py

# OU utiliser le fichier .spec directement
pyinstaller pokemon_dataset_generator.spec
```

---

## 📂 Résultats Générés

Après exécution, vous trouverez :

```
dist/
├── Pokemon_Dataset_Generator.exe          # 📦 Executable seul (~200 MB)
└── Pokemon_Dataset_Generator_Portable/    # 📦 Package complet
    ├── Pokemon_Dataset_Generator.exe
    ├── cards_info.xlsx
    ├── README_PORTABLE.txt
    ├── README.md
    ├── requirements.txt
    ├── images/                            # Dossier vide (à remplir)
    ├── output/                            # Dossiers de sortie
    ├── fakeimg/
    ├── fakeimg_augmented/
    └── examples/
```

---

## 🚀 Lancement Sans Console

### Option 1 : Batch Silencieux

```batch
Pokemon_Dataset_Generator.bat
```

Utilise `pythonw.exe` pour lancer sans fenêtre console.

### Option 2 : Executable

```batch
dist\Pokemon_Dataset_Generator.exe
```

Version compilée sans console (option `--windowed`).

---

## 🔧 Personnalisation

### Ajouter une Icône

1. Créez ou obtenez un fichier `.ico` (icône Windows)
2. Placez-le dans le dossier (ex: `pokemon.ico`)
3. Éditez `create_exe.py` ligne ~75 :

```python
"--icon=pokemon.ico",  # Au lieu de "--icon=NONE"
```

### Inclure des Fichiers Supplémentaires

Éditez `create_exe.py` dans la section `files_to_copy` :

```python
files_to_copy = [
    "cards_info.xlsx",
    "README.md",
    "requirements.txt",
    "mon_fichier.txt",  # Ajoutez ici
]
```

### Ajuster la Taille de l'Exe

**Option 1 : Utiliser UPX (compression)**

```python
# Dans pokemon_dataset_generator.spec
upx=True,  # Déjà activé par défaut
```

**Option 2 : Exclure des modules**

```python
# Dans pokemon_dataset_generator.spec
excludes=[
    'matplotlib',  # Si vous ne l'utilisez pas
    'pytest',
    'scipy.spatial.cKDTree',  # Modules lourds non utilisés
],
```

---

## ⚠️ Résolution de Problèmes

### Erreur : "PyInstaller n'est pas installé"

```batch
.venv\Scripts\activate
pip install pyinstaller
```

### Erreur : "Module cv2 non trouvé"

Vérifiez que OpenCV est installé dans l'environnement :

```batch
.venv\Scripts\activate
pip install opencv-python
```

### L'exe est trop lent au démarrage

Normal pour la première exécution. PyInstaller extrait les fichiers dans un dossier temporaire.

**Solution** : Utilisez `--onedir` au lieu de `--onefile` pour un démarrage plus rapide (mais plus de fichiers).

### Antivirus bloque l'exe

Les executables PyInstaller sont parfois détectés comme faux positifs.

**Solutions** :
1. Ajoutez une exception dans votre antivirus
2. Signez numériquement l'exe (certificat de code)
3. Utilisez `--onedir` au lieu de `--onefile`

### L'exe ne trouve pas cards_info.xlsx

Vérifiez que le fichier est bien inclus :

```python
# Dans create_exe.py
datas=[
    ('cards_info.xlsx', '.'),  # Doit être présent
]
```

---

## 📊 Comparaison des Options

| Option | Taille | Démarrage | Distribution | Console |
|--------|--------|-----------|--------------|---------|
| **Python + .bat** | ~500 MB | Rapide | Nécessite Python | Visible |
| **pythonw.exe + .bat** | ~500 MB | Rapide | Nécessite Python | Cachée |
| **PyInstaller --onefile** | ~200 MB | Lent (~5s) | Standalone | Cachée |
| **PyInstaller --onedir** | ~300 MB | Rapide | Standalone | Cachée |

**Recommandation** : 
- **Développement** : Python + .bat (avec console)
- **Distribution** : PyInstaller --onefile (sans console)

---

## 🎓 Technique : Comment ça marche ?

### PyInstaller

1. **Analyse** : Scanne `GUI_v2.py` et trouve toutes les dépendances
2. **Collection** : Copie tous les modules Python nécessaires
3. **Empaquetage** : 
   - `--onefile` : Crée un exe unique avec archive interne
   - `--onedir` : Crée un dossier avec exe + DLLs
4. **Bootloader** : Ajoute un mini-programme qui :
   - Extrait les fichiers dans un dossier temporaire
   - Lance l'interpréteur Python embarqué
   - Exécute le script principal

### pythonw.exe vs python.exe

- `python.exe` : Lance avec console (fenêtre CMD)
- `pythonw.exe` : Lance sans console (mode GUI)

**Utilisé dans** : `run_gui_silent.bat`

### invisible.vbs

Script VBScript qui lance un batch sans afficher de fenêtre :

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """batch.bat""", 0, False
'              ^commande^      ^caché^
```

**Utilisé dans** : `Pokemon_Dataset_Generator.bat`

---

## 📚 Ressources

- **PyInstaller Documentation** : https://pyinstaller.org/
- **UPX Compression** : https://upx.github.io/
- **Code Signing** : https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools

---

## ✅ Checklist Distribution

Avant de distribuer votre exe :

- [ ] Testez l'exe sur une machine **sans Python installé**
- [ ] Vérifiez que `cards_info.xlsx` est bien inclus
- [ ] Testez toutes les fonctionnalités (augmentation, mosaïques, etc.)
- [ ] Vérifiez les chemins de fichiers (doivent être relatifs)
- [ ] Créez un README pour l'utilisateur final
- [ ] Testez avec Windows Defender / Antivirus
- [ ] Considérez la signature numérique (optionnel)
- [ ] Créez un fichier ZIP pour distribution

---

## 🎉 Résultat Final

**Version Portable Professionnelle** :

```
Pokemon_Dataset_Generator_v2.0.zip
└── Pokemon_Dataset_Generator_Portable/
    ├── Pokemon_Dataset_Generator.exe  ← Double-clic pour lancer
    ├── README_PORTABLE.txt
    ├── cards_info.xlsx
    └── [dossiers pour les données]
```

✨ **Aucune installation requise !**
✨ **Fonctionne sur Windows 10/11**
✨ **Prêt à partager**

---

**Date de création** : 30 octobre 2025  
**Version** : 2.0.1
