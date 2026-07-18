# 🚀 Installation Guide - Pokémon Dataset Generator

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025

---

## 📋 Prérequis Système

### Configuration Minimale

| Composant | Minimum | Recommandé | Notes |
|-----------|---------|------------|-------|
| **OS** | Windows 10 | Windows 11 | Linux/Mac supportés (sans .bat) |
| **CPU** | Intel i5 / Ryzen 5 | Intel i7 / Ryzen 7 | 4+ cores |
| **RAM** | 8 GB | 16 GB | 32 GB idéal (training) |
| **GPU** | Aucun (CPU only) | RTX 3060 12GB | CUDA 11.8+ |
| **Stockage** | 10 GB libre | 50+ GB SSD | Datasets volumineux |
| **Python** | 3.10 | 3.12 | 3.13+ INTERDIT |

### Logiciels Requis

1. **Python 3.10-3.12** ⚠️ PAS 3.13+
   - Télécharger : [python.org/downloads](https://www.python.org/downloads/)
   - ✅ Cocher "Add Python to PATH" lors installation
   - ✅ Cocher "pip" lors installation

2. **Git** (optionnel, pour clonage repo)
   - Télécharger : [git-scm.com](https://git-scm.com/)

3. **NVIDIA Drivers** (si GPU)
   - RTX 30xx/40xx/50xx : [nvidia.com/drivers](https://www.nvidia.com/Download/index.aspx)
   - CUDA auto-installé avec PyTorch

---

## ⚡ Installation Rapide (Recommandée)

### Windows

**Étape 1 : Cloner ou télécharger projet**
```batch
# Option A : Git clone
git clone https://github.com/username/pok.git
cd pok

# Option B : Télécharger ZIP
# Extraire pok-main.zip → C:\DATA\pok
```

**Étape 2 : Lancer installeur automatique**
```batch
# Double-cliquer sur :
INSTALL.bat

# OU en ligne de commande :
cd C:\DATA\pok
INSTALL.bat
```

**Ce que fait INSTALL.bat** :
1. ✅ Vérifie Python 3.10-3.12
2. ✅ Crée environnement virtuel `.venv/`
3. ✅ Installe dépendances (`config/requirements.txt`)
4. ✅ Détecte GPU et installe PyTorch CUDA approprié
5. ✅ Vérifie installation avec tests

**Durée** : 5-10 minutes (selon connexion internet)

**Étape 3 : Vérifier installation**
```batch
# Lancer application
START.bat
```

**Si GUI s'ouvre** : ✅ Installation réussie !

---

### Linux / macOS

**Étape 1 : Cloner projet**
```bash
git clone https://github.com/username/pok.git
cd pok
```

**Étape 2 : Installation manuelle**
```bash
# Créer venv
python3 -m venv .venv

# Activer venv
source .venv/bin/activate  # Linux/Mac
# OU
.venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r config/requirements.txt

# Si GPU NVIDIA (CUDA 12.4)
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

**Étape 3 : Lancer application**
```bash
source .venv/bin/activate
python GUI_v3.1_modern.py
```

---

## 🔧 Installation Détaillée (Manuelle)

### 1. Vérifier Python

**Vérifier version installée** :
```batch
python --version
# Doit afficher : Python 3.10.x, 3.11.x ou 3.12.x
```

**Si Python 3.13+ installé** :
⚠️ **NumPy 2.0+ incompatible avec imgaug !**

**Solutions** :
- **Option A** : Désinstaller Python 3.13, installer Python 3.12
- **Option B** : Utiliser `py` launcher (Windows)
  ```batch
  py -3.12 --version  # Force Python 3.12
  ```

---

### 2. Créer Environnement Virtuel

**Pourquoi venv ?**
- ✅ Isole dépendances du projet
- ✅ Évite conflits avec autres projets Python
- ✅ Permet versions spécifiques (NumPy < 2.0)

**Création venv** :
```batch
# Windows
python -m venv .venv

# Linux/Mac
python3 -m venv .venv
```

**Activer venv** :
```batch
# Windows
call .venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

**Vérifier activation** :
```batch
# Prompt doit afficher : (.venv)
# Vérifier chemin Python
python -c "import sys; print(sys.prefix)"
# Doit afficher : C:\DATA\pok\.venv
```

---

### 3. Installer Dépendances de Base

**requirements.txt principal** :
```batch
pip install -r config/requirements.txt
```

**Contenu `config/requirements.txt`** :
```
# Core
numpy<2.0           # CRITIQUE : NumPy 1.x obligatoire
opencv-python<4.10.0
Pillow>=10.0.0
PyYAML>=6.0

# Augmentation
imgaug>=0.4.0
albumentations>=2.0

# Deep Learning
ultralytics>=8.3.0  # YOLOv8 + YOLO11
torch>=2.0.0        # PyTorch (CPU par défaut)
torchvision>=0.15.0

# GUI
customtkinter>=5.2.0
tkinterdnd2>=0.3.0

# API & Utils
requests>=2.31.0
tqdm>=4.66.0
pandas>=2.0.0

# Scientific
scipy<1.14
scikit-image<0.23
```

---

### 4. Installer PyTorch avec GPU (Optionnel)

**⚠️ IMPORTANT** : PyTorch CPU installé par défaut. Pour GPU, suivre ci-dessous.

**Détecter GPU** :
```batch
# Windows
wmic path win32_VideoController get name
# Chercher : NVIDIA GeForce RTX

# Linux
lspci | grep -i nvidia
```

**Installation selon GPU** :

#### RTX 40xx / 50xx (CUDA 12.4)
```batch
pip uninstall torch torchvision torchaudio
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

#### RTX 30xx (CUDA 11.8)
```batch
pip uninstall torch torchvision torchaudio
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### AMD GPU (ROCm, Linux uniquement)
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.2
```

#### Apple Silicon (MPS)
```bash
pip3 install torch torchvision
# MPS détecté automatiquement sur M1/M2/M3
```

**Vérifier CUDA** :
```batch
python -c "import torch; print(torch.cuda.is_available())"
# Doit afficher : True (si GPU NVIDIA)

python -c "import torch; print(torch.cuda.get_device_name(0))"
# Affiche : NVIDIA GeForce RTX 3060
```

---

### 5. Dépendances Optionnelles

**Training avancé** :
```batch
pip install -r config/requirements_training.txt
```

**Contenu `requirements_training.txt`** :
```
tensorboard>=2.15.0
wandb>=0.16.0
comet-ml>=3.35.0
```

**Extras utiles** :
```batch
pip install -r config/requirements_extra.txt
```

**Contenu `requirements_extra.txt`** :
```
jupyter>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.18.0
```

---

## ✅ Vérification Installation

### Tests Automatiques

**Test complet** :
```batch
scripts\run_all_tests.bat
```

**Tests individuels** :

**1. Test GPU/CUDA** :
```batch
scripts\run_test.bat test_cuda
```
**Output attendu** :
```
✅ CUDA disponible : True
✅ GPU détecté : NVIDIA GeForce RTX 3060
✅ VRAM disponible : 12 GB
```

**2. Test intégrité projet** :
```batch
scripts\run_test.bat test_project_integrity
```
**Vérifie** :
- Structure dossiers
- Fichiers requis
- Imports Python

**3. Test imports** :
```batch
python -c "import torch, ultralytics, imgaug, customtkinter; print('✅ All imports OK')"
```

---

### Lancer Application

**Méthode 1 : Lanceur automatique (recommandé)**
```batch
START.bat
```

**Méthode 2 : Manuelle avec venv**
```batch
call .venv\Scripts\activate.bat
python GUI_v3.1_modern.py
```

**Méthode 3 : Sans venv (déconseillé)**
```batch
python GUI_v3.1_modern.py
```

**Si GUI s'ouvre correctement** : ✅ Installation réussie !

---

## 🐛 Troubleshooting Installation

### Problème 1 : "python: command not found"

**Cause** : Python pas ajouté au PATH

**Solutions** :
1. **Réinstaller Python** avec "Add to PATH" coché
2. **Ajouter manuellement au PATH** :
   - Panneau de configuration → Système → Variables d'environnement
   - PATH → Ajouter : `C:\Python312\` et `C:\Python312\Scripts\`

---

### Problème 2 : "ModuleNotFoundError: No module named 'xxx'"

**Cause** : Dépendance pas installée ou venv pas activé

**Solutions** :
```batch
# Vérifier venv activé
echo %VIRTUAL_ENV%
# Doit afficher : C:\DATA\pok\.venv

# Réinstaller dépendances
pip install -r config/requirements.txt
```

---

### Problème 3 : "NumPy 2.0 incompatible"

**Cause** : NumPy 2.0+ installé (incompatible imgaug)

**Solution** :
```batch
pip uninstall numpy
pip install "numpy<2.0"
pip install imgaug
```

---

### Problème 4 : PyTorch GPU pas détecté

**Vérifier installation** :
```batch
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

**Si CUDA False** :
1. **Vérifier drivers NVIDIA à jour**
2. **Réinstaller PyTorch GPU** (voir section 4 ci-dessus)
3. **Vérifier CUDA version compatible** :
   ```batch
   nvidia-smi  # Affiche CUDA version supportée
   ```

---

### Problème 5 : Permission denied lors création venv

**Cause** : Droits insuffisants

**Solutions** :
1. **Lancer CMD en Administrateur**
2. **Changer politique exécution** (PowerShell) :
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

---

## 🔄 Mise à Jour

### Mettre à jour le projet

**Option A : Git pull (si cloné avec Git)**
```batch
cd C:\DATA\pok
git pull origin main
```

**Option B : Télécharger nouvelle version ZIP**
- Extraire dans nouveau dossier
- Copier `images/`, `models/`, `output/` depuis ancienne version

### Mettre à jour dépendances

```batch
call .venv\Scripts\activate.bat
pip install --upgrade -r config/requirements.txt
```

**Attention** : Ne jamais faire `pip install --upgrade numpy` (risque NumPy 2.0)

### Réinstaller complètement

```batch
# Supprimer venv
rmdir /s /q .venv

# Réinstaller
INSTALL.bat
```

---

## 📦 Installation avec PyInstaller (.exe)

**Créer exécutable standalone** (Windows uniquement) :

```batch
call .venv\Scripts\activate.bat
pip install pyinstaller
pyinstaller config/pokemon_dataset_generator.spec
```

**Output** : `dist/Pokemon_Dataset_Generator.exe`

**Avantages** :
- ✅ Pas besoin Python installé
- ✅ Distributable (1 fichier .exe)

**Inconvénients** :
- ❌ Fichier volumineux (~500 MB)
- ❌ Compilation longue (10-15 min)

**Documentation complète** : `docs/CREATION_EXE.md`

---

## 🌐 Installation sur serveur (Headless)

**Pour entraînement sans GUI** :

```bash
# Installation minimale
pip install ultralytics torch torchvision numpy opencv-python pillow pyyaml

# Lancer training CLI
python core/training_manager.py --data output/yolov8/data.yaml --epochs 100
```

**Détection sans GUI** :
```python
from ultralytics import YOLO
model = YOLO('runs/detect/train/weights/best.pt')
results = model('image.jpg')
```

---

**Installation terminée !** 🎉

**Prochaines étapes** :
1. Consulter `README.md` (racine) : Quick start
2. Lire `docs/USER_GUIDE.md` : Guide utilisateur complet
3. Suivre `docs/guides/GETTING_STARTED.md` : Premier workflow

**Aide supplémentaire** :
- FAQ : `docs/FAQ.md`
- Troubleshooting : `docs/guides/TROUBLESHOOTING.md`
- Documentation complète : `docs/README_COMPLET.md`
