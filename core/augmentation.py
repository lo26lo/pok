#!/usr/bin/env python3
import os
import sys
import cv2
import pandas as pd
from glob import glob
import re
import random
import time
import argparse
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# Import centralized utilities (functions, patterns, config)
from core.utils import (
    safe_print,
    extract_card_number,
    load_card_data,
    resize_cards,
    PATTERN_NEW_FORMAT,
    PATTERN_OLD_FORMAT,
    PATTERN_FALLBACK_1,
    PATTERN_FALLBACK_2,
    CONFIG
)

import imgaug.augmenters as iaa

# Taille cible pour redimensionner les images (utilise la config centralisée)
TARGET_SIZE = CONFIG['target_size']

# Configuration par défaut (peut être surchargée par arguments CLI)
DEFAULT_NUM_AUG = 30
DEFAULT_SOURCE = "images"
DEFAULT_TARGET = "augmented"

# Sera configuré dynamiquement
BASE_IMAGES_DIR = "images"

# Configuration des dossiers de sortie (par défaut)
AUG_OUTPUT_DIR = os.path.join("output", "augmented")
AUG_IMAGES_DIR = os.path.join(AUG_OUTPUT_DIR, "images")
AUG_LABELS_DIR = os.path.join(AUG_OUTPUT_DIR, "labels")

# Création des dossiers s'ils n'existent pas
os.makedirs(AUG_IMAGES_DIR, exist_ok=True)
os.makedirs(AUG_LABELS_DIR, exist_ok=True)

# Pipeline d'augmentation avec imgaug - VERSION AMÉLIORÉE (plus de variété)
# Applique 2 à 5 transformations aléatoires parmi une liste étendue
seq = iaa.SomeOf((2, 5), [
    # Luminosité et contraste
    iaa.Add((-20, 20)),                            # Brightness
    iaa.Multiply((0.8, 1.2)),                      # Contrast multiplier
    iaa.LinearContrast((0.6, 1.6)),                # Linear contrast
    iaa.GammaContrast((0.7, 1.5)),                 # Gamma contrast
    
    # Couleurs
    iaa.AddToHueAndSaturation((-30, 30)),          # Hue/Saturation
    iaa.ChangeColorTemperature((3000, 10000)),     # Temperature
    iaa.MultiplyHueAndSaturation((0.8, 1.2)),      # Saturation multiply
    
    # Flou et netteté
    iaa.GaussianBlur((0, 2.0)),                    # Blur
    iaa.AverageBlur(k=(1, 5)),                     # Average blur
    iaa.Sharpen(alpha=(0, 0.5), lightness=(0.8, 1.3)),  # Sharpen
    
    # Bruit
    iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),     # Gaussian noise
    iaa.ImpulseNoise(0.02),                             # Salt & pepper
    iaa.SaltAndPepper(0.01),                            # Salt and pepper
    
    # Effets visuels
    iaa.imgcorruptlike.Fog(severity=(1, 2)),       # Fog (réduit)
    iaa.Posterize((5, 8)),                         # Posterize
    iaa.Emboss(alpha=(0, 0.3), strength=(0.5, 1.5)),    # Emboss (réduit)
    iaa.EdgeDetect(alpha=(0.0, 0.3)),              # Edge detect (réduit)
    
    # Compression JPEG (simule une photo de mauvaise qualité)
    iaa.JpegCompression(compression=(50, 99)),
    
    # Élastique (légère déformation)
    iaa.ElasticTransformation(alpha=(0, 5), sigma=0.5),
], random_order=True)

def main():
    # Chargement depuis YAML uniquement
    import os
    global BASE_IMAGES_DIR, AUG_OUTPUT_DIR, AUG_IMAGES_DIR, AUG_LABELS_DIR
    
    # Parser les arguments CLI
    parser = argparse.ArgumentParser(description="Data augmentation for Pokemon cards")
    parser.add_argument("--num_aug", type=int, default=DEFAULT_NUM_AUG,
                       help="Nombre d'augmentations par image de base")
    parser.add_argument("--source", type=str, default=DEFAULT_SOURCE, 
                       choices=["images", "holographic"],
                       help="Source des images : 'images' (originales) ou 'holographic' (augmentations holographiques)")
    parser.add_argument("--target", type=str, default=DEFAULT_TARGET,
                       choices=["augmented", "images_aug"],
                       help="Destination des images augmentées")
    args = parser.parse_args()
    
    # Configuration du répertoire source selon le paramètre --source
    if args.source == "holographic":
        BASE_IMAGES_DIR = os.path.join("output", "holographic")
    else:
        BASE_IMAGES_DIR = "images"
    
    # Configuration des dossiers de sortie selon le paramètre --target
    if args.target == "augmented":
        AUG_OUTPUT_DIR = os.path.join("output", "augmented")
        AUG_IMAGES_DIR = os.path.join(AUG_OUTPUT_DIR, "images")
        AUG_LABELS_DIR = os.path.join(AUG_OUTPUT_DIR, "labels")
    else:
        AUG_OUTPUT_DIR = "images_aug"
        AUG_IMAGES_DIR = "images_aug"
        AUG_LABELS_DIR = os.path.join("images_aug_labels")
    
    # Création des dossiers
    os.makedirs(AUG_IMAGES_DIR, exist_ok=True)
    os.makedirs(AUG_LABELS_DIR, exist_ok=True)
    
    yaml_path = "models/cards_database.yaml"
    
    if not os.path.exists(yaml_path):
        print(f"❌ Fichier YAML non trouvé: {yaml_path}")
        print("   Créez-le avec: scripts\\run_script.bat init_prices_simple")
        return
    
    card_dict, class_map = load_card_data(yaml_path)
    
    # Collecte des images de base depuis le répertoire "images"
    image_paths = []
    image_paths += glob(os.path.join(BASE_IMAGES_DIR, "*.jpg"))
    image_paths += glob(os.path.join(BASE_IMAGES_DIR, "*.png"))
    resized_images = resize_cards(image_paths, TARGET_SIZE)
    if not resized_images:
        print("Aucune image valide trouvée dans le répertoire de base!")
        return
    NUM_AUG_PER_IMAGE = args.num_aug
    aug_index = 1
    for img, path in resized_images:
        base_name = os.path.splitext(os.path.basename(path))[0]
        card_number = extract_card_number(base_name)
        if card_number is None or card_number not in class_map:
            continue
        # Pour YOLO, la première classe (1 dans l'Excel) devient 0
        class_id = class_map[card_number] - 1
        for i in range(NUM_AUG_PER_IMAGE):
            # Réinitialiser le seed aléatoire pour chaque augmentation (plus de variété)
            np.random.seed(int(time.time() * 1000000) % (2**31) + i)
            random.seed(int(time.time() * 1000000) % (2**31) + i)
            
            aug_img = seq(image=img)
            out_img_name = f"{base_name}_aug_{i:03d}.png"
            out_img_path = os.path.join(AUG_IMAGES_DIR, out_img_name)
            cv2.imwrite(out_img_path, aug_img)
            out_label_name = f"{base_name}_aug_{i:03d}.txt"
            out_label_path = os.path.join(AUG_LABELS_DIR, out_label_name)
            annotation_line = f"{class_id} 0.5 0.5 1.0 1.0"
            with open(out_label_path, "w") as f:
                f.write(annotation_line)
            aug_index += 1
    yaml_path = os.path.join(AUG_OUTPUT_DIR, "data.yaml")
    with open(yaml_path, "w") as f:
        if args.target == "augmented":
            f.write("train: images\n")
            f.write("val: images\n")
        else:
            f.write("train: images_aug\n")
            f.write("val: images_aug\n")
        nc = len(class_map)
        f.write(f"nc: {nc}\n")
        f.write("names:\n")
        names_list = [None] * nc
        for card_num, cid in class_map.items():
            names_list[cid - 1] = card_dict[card_num]
        for name in names_list:
            f.write(f"  - {name}\n")
    print(f"Dataset d'augmentation généré avec {aug_index - 1} images.")
    print(f"Le fichier YAML est situé à : {yaml_path}")

if __name__ == "__main__":
    main()
