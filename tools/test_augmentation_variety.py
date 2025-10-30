#!/usr/bin/env python3
"""
Script de test pour visualiser la variété des augmentations.
Génère 10 augmentations d'une seule carte pour comparaison visuelle.
"""
import os
import sys
import cv2
import numpy as np
import random
import time
from glob import glob

# Patch NumPy pour imgaug
if not hasattr(np, 'bool'):
    np.bool = np.bool_
if not hasattr(np, 'int'):
    np.int = np.int_
if not hasattr(np, 'float'):
    np.float = np.float_

import imgaug.augmenters as iaa

# Pipeline d'augmentation amélioré (identique à augmentation.py)
seq = iaa.SomeOf((2, 5), [
    # Luminosité et contraste
    iaa.Add((-20, 20)),
    iaa.Multiply((0.8, 1.2)),
    iaa.LinearContrast((0.6, 1.6)),
    iaa.GammaContrast((0.7, 1.5)),
    
    # Couleurs
    iaa.AddToHueAndSaturation((-30, 30)),
    iaa.ChangeColorTemperature((3000, 10000)),
    iaa.MultiplyHueAndSaturation((0.8, 1.2)),
    
    # Flou et netteté
    iaa.GaussianBlur((0, 2.0)),
    iaa.AverageBlur(k=(1, 5)),
    iaa.Sharpen(alpha=(0, 0.5), lightness=(0.8, 1.3)),
    
    # Bruit
    iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),
    iaa.ImpulseNoise(0.02),
    iaa.SaltAndPepper(0.01),
    
    # Effets visuels
    iaa.imgcorruptlike.Fog(severity=(1, 2)),
    iaa.Posterize((5, 8)),
    iaa.Emboss(alpha=(0, 0.3), strength=(0.5, 1.5)),
    iaa.EdgeDetect(alpha=(0.0, 0.3)),
    iaa.JpegCompression(compression=(50, 99)),
    iaa.ElasticTransformation(alpha=(0, 5), sigma=0.5),
], random_order=True)

def main():
    # Chercher une image dans le dossier images/
    image_paths = glob(os.path.join("images", "*.png")) + glob(os.path.join("images", "*.jpg"))
    
    if not image_paths:
        print("❌ Aucune image trouvée dans le dossier 'images/'")
        return
    
    # Prendre la première image
    test_image_path = image_paths[0]
    print(f"🎯 Test avec l'image : {os.path.basename(test_image_path)}")
    
    # Charger et redimensionner
    img = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"❌ Impossible de charger l'image")
        return
    
    # Convertir RGBA en RGB si nécessaire
    if len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    img = cv2.resize(img, (280, 380), interpolation=cv2.INTER_AREA)
    
    # Créer dossier de test
    test_dir = "test_augmentation_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # Sauvegarder l'originale
    cv2.imwrite(os.path.join(test_dir, "00_original.png"), img)
    print(f"💾 Image originale sauvegardée")
    
    # Générer 10 augmentations
    print(f"\n🎨 Génération de 10 augmentations variées...")
    for i in range(10):
        # Seed aléatoire différent pour chaque augmentation
        np.random.seed(int(time.time() * 1000000) % (2**31) + i)
        random.seed(int(time.time() * 1000000) % (2**31) + i)
        
        aug_img = seq(image=img)
        out_path = os.path.join(test_dir, f"{i+1:02d}_augmented.png")
        cv2.imwrite(out_path, aug_img)
        print(f"  ✅ Augmentation {i+1}/10 générée")
    
    print(f"\n✅ Test terminé !")
    print(f"📂 Vérifiez les résultats dans : {test_dir}/")
    print(f"💡 Comparez les 10 images pour voir la variété")

if __name__ == "__main__":
    main()
