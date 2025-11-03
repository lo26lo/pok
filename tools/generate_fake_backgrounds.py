#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour générer des images de fond (fake backgrounds) pour mosaic.py
Compatible Windows avec encodage UTF-8
"""
import cv2
import numpy as np
import os
import sys
import argparse

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Parser les arguments
parser = argparse.ArgumentParser(description='Generate fake background images')
parser.add_argument('--count', type=int, default=100, help='Number of images to generate')
parser.add_argument('--output', type=str, default='fakeimg', help='Output directory')
parser.add_argument('--min-noise', type=int, default=20, help='Minimum noise intensity (0-100)')
parser.add_argument('--max-noise', type=int, default=60, help='Maximum noise intensity (0-100)')
args = parser.parse_args()

FAKE_DIR = args.output
os.makedirs(FAKE_DIR, exist_ok=True)

# Taille des images de fond
WIDTH, HEIGHT = 1920, 1080

print(f"[OK] Generating {args.count} fake backgrounds...")
print(f"[OK] Output directory: {FAKE_DIR}")
print(f"[OK] Noise range: {args.min_noise}-{args.max_noise}")

# Générer les images de base variées
base_images = []

# 1-10. Fonds unis avec variations
colors = [
    (255, 255, 255),  # Blanc
    (0, 0, 0),        # Noir
    (128, 128, 128),  # Gris
    (230, 200, 150),  # Bleu clair (BGR)
    (180, 220, 180),  # Vert clair
    (150, 150, 230),  # Rouge clair
    (200, 230, 230),  # Jaune clair
    (220, 180, 150),  # Cyan clair
    (180, 150, 220),  # Magenta clair
    (200, 200, 200),  # Gris clair
]

for i, color in enumerate(colors):
    img = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
    img[:, :] = color
    base_images.append(img)

# 11-20. Gradients
for i in range(10):
    gradient = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    if i < 5:
        # Gradients horizontaux
        for x in range(WIDTH):
            gradient[:, x] = int(255 * x / WIDTH)
    else:
        # Gradients verticaux
        for y in range(HEIGHT):
            gradient[y, :] = int(255 * y / HEIGHT)
    base_images.append(gradient)

# Générer le nombre demandé d'images avec variations
for idx in range(args.count):
    # Choisir une image de base
    base_img = base_images[idx % len(base_images)].copy()
    
    # Ajouter du bruit aléatoire
    noise_intensity = np.random.randint(args.min_noise, args.max_noise)
    noise = np.random.randint(-noise_intensity, noise_intensity, base_img.shape, dtype=np.int16)
    img_with_noise = np.clip(base_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Sauvegarder
    filename = os.path.join(FAKE_DIR, f"fake_bg_{idx:04d}.png")
    cv2.imwrite(filename, img_with_noise)
    
    # Afficher la progression tous les 10%
    if (idx + 1) % max(1, args.count // 10) == 0:
        progress = int((idx + 1) / args.count * 100)
        print(f"[{progress:3d}%] Generated {idx + 1}/{args.count} images")

print(f"[OK] {args.count} fake backgrounds generated in '{FAKE_DIR}/'")
