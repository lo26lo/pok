#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pré-annotation assistée du set de validation réel (F08).

Pour chaque photo de datasets/real_val/images/ SANS label, fait prédire le
modèle courant et écrit un fichier YOLO dans labels/. Ces fichiers sont un
BROUILLON : il faut les corriger à la main avant d'évaluer (les erreurs du
modèle deviendraient la vérité terrain !).

Usage :
    python tools/preannotate_real_val.py
    python tools/preannotate_real_val.py --model autre.pt --conf 0.4 --overwrite
"""
import argparse
import os
import sys

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.real_validation import DEFAULT_REAL_VAL_DIR, list_images  # noqa: E402
from core.utils import PATHS  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='Pre-annotate real validation photos')
    parser.add_argument('--model',
                        default=PATHS['files'].get(
                            'best_model',
                            'runs/train/pokemon_detector/weights/best.pt'))
    parser.add_argument('--dir', default=DEFAULT_REAL_VAL_DIR)
    parser.add_argument('--conf', type=float, default=0.30,
                        help='Seuil de confiance des prédictions (défaut 0.30)')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--overwrite', action='store_true',
                        help='Réécrire aussi les labels existants')
    args = parser.parse_args()

    if not os.path.exists(args.model):
        print(f"[ERREUR] Modèle introuvable: {args.model}")
        sys.exit(1)

    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERREUR] ultralytics non installé (pip install ultralytics)")
        sys.exit(1)

    images_dir = os.path.join(args.dir, "images")
    labels_dir = os.path.join(args.dir, "labels")
    os.makedirs(labels_dir, exist_ok=True)

    images = list_images(images_dir)
    if not images:
        print(f"[INFO] Aucune image dans {images_dir} — déposez vos photos d'abord")
        sys.exit(0)

    todo = []
    for img in images:
        stem = os.path.splitext(os.path.basename(img))[0]
        label = os.path.join(labels_dir, f"{stem}.txt")
        if args.overwrite or not os.path.exists(label):
            todo.append((img, label))

    print(f"[OK] {len(images)} photos, {len(todo)} à pré-annoter "
          f"(modèle: {args.model}, conf >= {args.conf})")
    if not todo:
        sys.exit(0)

    model = YOLO(args.model)
    written = 0
    for img_path, label_path in todo:
        results = model.predict(img_path, conf=args.conf, device=args.device,
                                verbose=False)
        lines = []
        for box in results[0].boxes:
            cls = int(box.cls.item())
            cx, cy, w, h = box.xywhn[0].tolist()
            lines.append(f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        with open(label_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        written += 1
        print(f"  [{written}/{len(todo)}] {os.path.basename(img_path)}: "
              f"{len(lines)} carte(s) détectée(s)")

    print(f"[OK] {written} brouillons écrits dans {labels_dir}/")
    print("[!] CORRIGEZ-LES À LA MAIN avant toute évaluation, puis lancez:")
    print("    python core/real_validation.py --check")


if __name__ == "__main__":
    main()
