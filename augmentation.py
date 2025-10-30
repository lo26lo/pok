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

# Patch de compatibilité NumPy pour imgaug (doit être avant l'import imgaug)
if not hasattr(np, 'bool'):
    np.bool = np.bool_
if not hasattr(np, 'int'):
    np.int = np.int_
if not hasattr(np, 'float'):
    np.float = np.float_
if not hasattr(np, 'complex'):
    np.complex = np.complex_
if not hasattr(np, 'object'):
    np.object = np.object_
if not hasattr(np, 'str'):
    np.str = np.str_

import imgaug.augmenters as iaa

# Taille cible pour redimensionner les images (comme dans le script mosaic)
TARGET_SIZE = (280, 380)
# Répertoire contenant les cartes de base (non-augmentées)
BASE_IMAGES_DIR = "images"

# Parseur d'arguments
parser = argparse.ArgumentParser(description="Data augmentation for Pokemon cards")
parser.add_argument("--num_aug", type=int, default=30, help="Nombre d'augmentations par image de base")
parser.add_argument("--target", type=str, default="augmented", choices=["augmented", "images_aug"],
                    help="Destination des images augmentées")
args = parser.parse_args()

# Configuration des dossiers de sortie selon le paramètre --target
if args.target == "augmented":
    AUG_OUTPUT_DIR = os.path.join("output", "augmented")
    AUG_IMAGES_DIR = os.path.join(AUG_OUTPUT_DIR, "images")
    AUG_LABELS_DIR = os.path.join(AUG_OUTPUT_DIR, "labels")
else:
    AUG_OUTPUT_DIR = "images_aug"
    AUG_IMAGES_DIR = "images_aug"
    AUG_LABELS_DIR = os.path.join("images_aug_labels")

# Création des dossiers s'ils n'existent pas
os.makedirs(AUG_IMAGES_DIR, exist_ok=True)
os.makedirs(AUG_LABELS_DIR, exist_ok=True)

def load_card_data(excel_path):
    df = pd.read_excel(excel_path, usecols=["Set #", "Name"])
    card_dict = {}
    class_map = {}
    class_id = 1  # On commence à 1 (on convertira en 0-index pour YOLO)
    for _, row in df.iterrows():
        number = row["Set #"].split('/')[0].zfill(3)
        name = row["Name"].replace(" ", "_")
        if number not in card_dict:
            card_dict[number] = name
            class_map[number] = class_id
            class_id += 1
    return card_dict, class_map

def extract_card_number(filename):
    """
    Extrait le numéro de carte à partir du nom de fichier.
    Supporte plusieurs formats:
    - pokemon_en_001_xyz.jpg -> "001"
    - SSP_001_R_EN_SM.png -> "001"
    - card_001.jpg -> "001"
    """
    # Format: _en_XXX_ (ancien format)
    match = re.search(r'_en_(\d{3})_', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Format: XXX_XXX_XXX (nouveau format, ex: SSP_001_R_EN_SM.png)
    match = re.search(r'_(\d{3})_', filename)
    if match:
        return match.group(1)
    
    # Format: XXX au début ou dans le nom
    match = re.search(r'(\d{3})', filename)
    if match:
        return match.group(1)
    
    return None

def resize_cards(image_paths, target_size=TARGET_SIZE):
    resized_images = []
    for img_path in image_paths:
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue
        
        # Convertir RGBA en RGB si nécessaire
        if len(img.shape) == 3 and img.shape[2] == 4:
            # Image a un canal alpha, le convertir en RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        resized_images.append((img, img_path))
    return resized_images

# Pipeline d'augmentation avec imgaug (sans rotation)
seq = iaa.SomeOf((1, 3), [
    iaa.Add((-10, 10)),                    # Ajoute une valeur constante aux pixels
    iaa.Multiply((0.9, 1.1)),               # Multiplie les valeurs des pixels
    iaa.GaussianBlur((0, 3.0)),             # Flou gaussien
    iaa.AddToHueAndSaturation((-20, 20)),    # Modification de la teinte et saturation
    iaa.LinearContrast((0.75, 1.5)),         # Modification du contraste
    iaa.EdgeDetect(alpha=(0.0, 0.7)),         # Détection d'arêtes
    iaa.imgcorruptlike.Fog(severity=(1, 3)),   # Simule du brouillard
    iaa.Posterize((4, 8)),                   # Réduction du nombre de bits par canal (effet artistique)
    iaa.Sharpen(alpha=(0, 1.0), lightness=(0.75, 1.5)),  # Accentue les contours
    iaa.Emboss(alpha=(0, 1.0), strength=(0, 2.0))         # Effet emboss
], random_order=True)

def main():
    card_dict, class_map = load_card_data("cards_info.xlsx")
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
