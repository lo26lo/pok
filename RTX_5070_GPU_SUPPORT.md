# RTX 5070 GPU Support - Important Notice

## ⚠️ Problème Actuel

Votre **NVIDIA RTX 5070 Laptop GPU** utilise l'architecture Blackwell avec **compute capability sm_120**.

La version **stable de PyTorch (2.6.0+cu124)** ne supporte actuellement que jusqu'à **sm_90**, ce qui cause l'erreur:
```
CUDA error: no kernel image is available for execution on the device
```

## 📊 Statut Actuel

✅ **CPU Training**: Fonctionne (stable mais plus lent)  
❌ **GPU Training**: Non supporté avec PyTorch stable  
⚠️ **GPU Training**: Possible avec PyTorch Nightly (instable)

## 🔧 Solutions Disponibles

### Option 1: Entraînement CPU (Recommandé pour la stabilité)

**Avantages:**
- ✅ Stable et fiable
- ✅ Fonctionne immédiatement
- ✅ Pas de risque de bugs

**Inconvénients:**
- ⏱️ Plus lent qu'avec GPU
- 🔋 Utilise le processeur

**Comment faire:**
Le code détecte automatiquement le problème et bascule vers CPU.
Lancez simplement l'entraînement depuis le GUI !

### Option 2: PyTorch Nightly (Pour utilisateurs avancés)

**Avantages:**
- 🚀 Utilise pleinement le GPU RTX 5070
- ⚡ Entraînement beaucoup plus rapide

**Inconvénients:**
- ⚠️ Version instable (nightly builds)
- 🐛 Peut avoir des bugs
- 🔄 Peut casser la compatibilité avec d'autres packages

**Installation:**
```batch
.\fix_pytorch_5070.bat
```
Puis choisissez l'option [1] pour installer PyTorch Nightly.

### Option 3: Attendre PyTorch 2.7+ Stable

**Meilleur choix à long terme:**
- Surveillez https://pytorch.org/get-started/locally/
- PyTorch 2.7+ stable ajoutera probablement le support sm_120
- Date de sortie: Non annoncée

## 🎯 Recommandation

**Pour la production / usage normal:**
➡️ **Utilisez l'entraînement CPU** (Option 1)
- Le code détecte automatiquement le problème
- Bascule vers CPU si GPU incompatible
- Vous verrez ce message:
  ```
  ⚠️  ATTENTION: GPU avec compute capability sm_120 détecté
  ⚠️  PyTorch stable ne supporte que jusqu'à sm_90
  ⚠️  Basculement automatique vers CPU
  ```

**Pour l'expérimentation / besoin de vitesse:**
➡️ **Testez PyTorch Nightly** (Option 2)
- Exécutez `.\fix_pytorch_5070.bat`
- Choisissez option [1]
- Testez l'entraînement
- Si problèmes, relancez le script et choisissez [2] pour revenir au CPU

## 📝 Détails Techniques

### Votre Configuration:
- **GPU**: NVIDIA GeForce RTX 5070 Laptop GPU
- **Compute Capability**: sm_120 (12.0)
- **Driver**: 573.24 (CUDA 12.8)
- **VRAM**: 8 GB

### Support PyTorch:
- **Stable (2.6.0+cu124)**: sm_50, sm_60, sm_61, sm_70, sm_75, sm_80, sm_86, sm_90
- **Nightly (dev)**: Peut inclure sm_120 (à vérifier)

### Pourquoi ce problème?

La RTX 5070 est une **toute nouvelle génération** de GPU (série 50xx, architecture Blackwell).
PyTorch stable a été compilé avant la sortie de cette architecture, donc les kernels CUDA pour sm_120 n'y sont pas inclus.

## ❓ FAQ

**Q: L'entraînement CPU est-il très lent?**
R: Plus lent que GPU, mais acceptable pour des petits modèles (yolov8n). Attendez-vous à 2-5x plus long.

**Q: PyTorch Nightly est-il sûr?**
R: C'est une version de développement. Généralement stable, mais peut avoir des bugs. Utilisez à vos risques.

**Q: Quand PyTorch stable supportera sm_120?**
R: Probablement dans PyTorch 2.7+, mais pas de date officielle annoncée.

**Q: Puis-je utiliser un GPU externe?**
R: Si vous avez un GPU plus ancien (RTX 30xx/40xx avec sm_86-90), PyTorch stable fonctionnera directement.

**Q: Le basculement automatique fonctionne-t-il toujours?**
R: Oui! Le code détecte la compute capability et bascule vers CPU automatiquement si nécessaire.

## 🔗 Ressources

- [PyTorch Get Started](https://pytorch.org/get-started/locally/)
- [NVIDIA CUDA Compute Capability](https://developer.nvidia.com/cuda-gpus)
- [PyTorch GitHub - Nightly Builds](https://github.com/pytorch/pytorch)

---

**Dernière mise à jour**: 4 Novembre 2025
**Votre GPU**: RTX 5070 Laptop (sm_120)
**PyTorch Stable**: 2.6.0+cu124 (supporte jusqu'à sm_90)
