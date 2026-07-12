#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère des fonds réalistes procéduraux (F04) sur disque.

Deux usages :
- Pré-générer N fonds dans un dossier (utilisables en background_mode 1
  via le dossier local, ou pour inspection) :
      python tools/generate_realistic_backgrounds.py --count 50 --output backgrounds/realistic
- Produire une galerie de contrôle visuel (planche contact, toutes catégories) :
      python tools/generate_realistic_backgrounds.py --gallery examples/backgrounds_gallery.jpg

Note : le background_mode 3 de core/mosaic_optimized.py génère les fonds
à la volée — ce script sert à l'inspection visuelle et aux usages hors pipeline.
"""
import argparse
import os
import sys

import cv2
import numpy as np

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import du générateur (exécutable depuis la racine du projet ou tools/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.background_generator import (BackgroundGenerator, CATEGORIES,
                                       apply_camera_effects)


def main():
    parser = argparse.ArgumentParser(description='Generate realistic procedural backgrounds')
    parser.add_argument('--count', type=int, default=20, help='Number of images to generate')
    parser.add_argument('--output', type=str, default='backgrounds/realistic', help='Output directory')
    parser.add_argument('--width', type=int, default=1920, help='Image width')
    parser.add_argument('--height', type=int, default=1080, help='Image height')
    parser.add_argument('--category', type=str, default=None, choices=CATEGORIES,
                        help='Force one category (default: random mix)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed (reproducible)')
    parser.add_argument('--camera-effects', action='store_true',
                        help='Apply photo effects (vignette, temperature) to saved images')
    parser.add_argument('--gallery', type=str, default=None,
                        help='Also write a contact sheet (all categories) to this path')
    args = parser.parse_args()

    gen = BackgroundGenerator(seed=args.seed)
    rng = np.random.default_rng(args.seed)

    if args.gallery:
        # Planche contact : 5 catégories x 3 variantes, vignettes 480x270
        thumb_w, thumb_h = 480, 270
        cols = 3
        rows = len(CATEGORIES)
        sheet = np.zeros((rows * thumb_h, cols * thumb_w, 3), np.uint8)
        for r, cat in enumerate(CATEGORIES):
            for c in range(cols):
                img = gen.generate(args.width, args.height, category=cat)
                if args.camera_effects:
                    img = apply_camera_effects(img, rng)
                thumb = cv2.resize(img, (thumb_w, thumb_h), interpolation=cv2.INTER_AREA)
                cv2.putText(thumb, cat, (12, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (255, 255, 255), 2, cv2.LINE_AA)
                sheet[r * thumb_h:(r + 1) * thumb_h, c * thumb_w:(c + 1) * thumb_w] = thumb
        gallery_dir = os.path.dirname(args.gallery)
        if gallery_dir:
            os.makedirs(gallery_dir, exist_ok=True)
        cv2.imwrite(args.gallery, sheet)
        print(f"[OK] Gallery written to {args.gallery}")

    if args.count > 0:
        os.makedirs(args.output, exist_ok=True)
        print(f"[OK] Generating {args.count} realistic backgrounds "
              f"({args.width}x{args.height}, category={args.category or 'mix'})...")
        for idx in range(args.count):
            img = gen.generate(args.width, args.height, category=args.category)
            if args.camera_effects:
                img = apply_camera_effects(img, rng)
            filename = os.path.join(args.output, f"realistic_bg_{idx:04d}.jpg")
            cv2.imwrite(filename, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
            if (idx + 1) % max(1, args.count // 10) == 0:
                progress = int((idx + 1) / args.count * 100)
                print(f"[{progress:3d}%] Generated {idx + 1}/{args.count} images")
        print(f"[OK] {args.count} realistic backgrounds generated in '{args.output}/'")


if __name__ == "__main__":
    main()
