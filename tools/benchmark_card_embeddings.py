#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
benchmark_card_embeddings.py — F01 : benchmark des embedders d'identification
==============================================================================

Compare les embedders de core/card_identifier.py (classic, dnn) sur des
images de cartes réelles : l'index est construit sur les images de référence
propres, puis des requêtes « type webcam » sont générées par perturbations
réalistes (perspective, rotation, éclairage, flou, bruit, JPEG, cadrage
imparfait, basse résolution) et on mesure top-1 / top-5 et la latence CPU.

Usage :
    python tools/benchmark_card_embeddings.py                       # défauts
    python tools/benchmark_card_embeddings.py --images images \\
        --n-cards 100 --queries 5 --methods classic dnn --seed 42

Par défaut les images viennent de backgrounds/original/ (245 cartes réelles
swsh7/sv08 committées dans le dépôt), à défaut de images/.
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.card_identifier import (  # noqa: E402
    CardIndex, card_id_from_filename, create_embedder, embed_reference,
    IMAGE_EXTENSIONS,
)


def make_query(image_bgr: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """
    Simule un crop webcam d'une carte bien cadrée à partir de l'image de
    référence : cadrage imparfait, perspective légère, rotation, éclairage,
    flou, bruit, compression JPEG, basse résolution.
    """
    img = image_bgr

    # 1. Cadrage imparfait : la bbox YOLO déborde ou rogne un peu (±4 %)
    h, w = img.shape[:2]
    pad = int(0.06 * min(h, w))
    canvas = np.full((h + 2 * pad, w + 2 * pad, 3), rng.integers(0, 255, 3,
                     dtype=np.uint8), dtype=np.uint8)
    canvas[pad:pad + h, pad:pad + w] = img
    jitter = lambda: int(rng.integers(-int(0.04 * min(h, w)), int(0.04 * min(h, w)) + 1))
    x0 = max(0, pad + jitter())
    y0 = max(0, pad + jitter())
    x1 = min(canvas.shape[1], pad + w + jitter())
    y1 = min(canvas.shape[0], pad + h + jitter())
    img = canvas[y0:y1, x0:x1]
    h, w = img.shape[:2]

    # 2. Perspective légère (coins déplacés jusqu'à 3 %)
    d = 0.03 * min(h, w)
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = src + rng.uniform(-d, d, size=(4, 2)).astype(np.float32)
    img = cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (w, h),
                              borderMode=cv2.BORDER_REPLICATE)

    # 3. Rotation ±8°
    angle = float(rng.uniform(-8, 8))
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

    # 4. Éclairage : exposition, contraste, température
    alpha = float(rng.uniform(0.7, 1.3))          # contraste
    beta = float(rng.uniform(-35, 35))            # exposition
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    temp = float(rng.uniform(-20, 20))            # température (B vs R)
    img = img.astype(np.float32)
    img[:, :, 0] = np.clip(img[:, :, 0] - temp, 0, 255)
    img[:, :, 2] = np.clip(img[:, :, 2] + temp, 0, 255)
    img = img.astype(np.uint8)

    # 5. Basse résolution type webcam (hauteur 180–420 px)
    target_h = int(rng.integers(180, 420))
    scale = target_h / img.shape[0]
    img = cv2.resize(img, (max(24, int(img.shape[1] * scale)), target_h),
                     interpolation=cv2.INTER_AREA)

    # 6. Flou et bruit
    if rng.random() < 0.7:
        k = int(rng.choice([3, 3, 5]))
        img = cv2.GaussianBlur(img, (k, k), 0)
    noise = rng.normal(0, rng.uniform(2, 8), img.shape).astype(np.float32)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # 7. Compression JPEG (qualité 40–90)
    q = int(rng.integers(40, 90))
    _, buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, q])
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def benchmark_method(method: str, references: list, queries: list,
                     model_path: str = None) -> dict:
    """Construit l'index sur les références et évalue les requêtes."""
    embedder = create_embedder(method, model_path)

    # Index (embeddings des références propres, moyenne des vues — comme
    # CardIndex.build en production)
    vectors = np.stack([embed_reference(embedder, img) for _, img in references])
    cards = [{"card_id": cid, "set_id": cid.rsplit('_', 1)[0],
              "local_id": cid.rsplit('_', 1)[1], "name": None, "file": ""}
             for cid, _ in references]
    index = CardIndex(vectors, cards,
                      {"version": 1, "method": method, "dim": embedder.dim,
                       "count": len(cards)})

    top1 = top5 = 0
    embed_times = []
    search_times = []
    for true_id, query_img in queries:
        t0 = time.perf_counter()
        vec = embedder.embed(query_img)
        t1 = time.perf_counter()
        neighbors = index.search(vec, k=5)
        t2 = time.perf_counter()
        embed_times.append(t1 - t0)
        search_times.append(t2 - t1)
        ids = [index.cards[i]["card_id"] for i, _ in neighbors]
        if ids and ids[0] == true_id:
            top1 += 1
        if true_id in ids:
            top5 += 1

    n = len(queries)
    return {
        "method": method,
        "backend": index.backend,
        "top1": top1 / n,
        "top5": top5 / n,
        "embed_ms": 1000 * float(np.mean(embed_times)),
        "embed_ms_p95": 1000 * float(np.percentile(embed_times, 95)),
        "search_ms": 1000 * float(np.mean(search_times)),
        "dim": embedder.dim,
        "n_queries": n,
        "n_cards": len(references),
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark des embedders F01")
    parser.add_argument("--images", default=None,
                        help="Dossier d'images de cartes (défaut: "
                             "backgrounds/original puis images/)")
    parser.add_argument("--n-cards", type=int, default=60,
                        help="Nombre de cartes de référence (défaut: 60)")
    parser.add_argument("--queries", type=int, default=5,
                        help="Requêtes perturbées par carte (défaut: 5)")
    parser.add_argument("--methods", nargs="+", default=["classic", "dnn"],
                        help="Embedders à comparer (défaut: classic dnn)")
    parser.add_argument("--model", default=None,
                        help="Chemin du modèle ONNX pour la méthode dnn")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    # Résoudre le dossier d'images
    if args.images:
        images_dir = Path(args.images)
    else:
        images_dir = Path("backgrounds/original")
        if not any(images_dir.glob("*.png")) if images_dir.is_dir() else True:
            images_dir = Path("images")
    if not images_dir.is_dir():
        print(f"❌ Dossier introuvable: {images_dir}")
        return 1

    files = sorted(p for p in images_dir.iterdir()
                   if p.suffix.lower() in IMAGE_EXTENSIONS
                   and card_id_from_filename(p.name))
    if len(files) < 10:
        print(f"❌ Trop peu de cartes dans {images_dir} ({len(files)} trouvées)")
        return 1

    rng = np.random.default_rng(args.seed)
    if len(files) > args.n_cards:
        files = [files[i] for i in
                 sorted(rng.choice(len(files), args.n_cards, replace=False))]

    print(f"📇 Références: {len(files)} cartes depuis {images_dir}")
    references = []
    seen = set()
    for path in files:
        cid = card_id_from_filename(path.name)
        if cid in seen:
            continue
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is not None:
            references.append((cid, img))
            seen.add(cid)

    print(f"🎥 Génération de {args.queries} requêtes webcam par carte "
          f"(seed={args.seed})...")
    queries = [(cid, make_query(img, rng))
               for cid, img in references
               for _ in range(args.queries)]

    print(f"\n{'méthode':<10} {'backend':<8} {'dim':>5} {'top-1':>8} "
          f"{'top-5':>8} {'embed ms':>9} {'p95 ms':>8} {'search ms':>10}")
    print("-" * 72)
    results = []
    for method in args.methods:
        try:
            r = benchmark_method(method, references, queries, args.model)
        except FileNotFoundError as e:
            print(f"{method:<10} ⏭️  ignoré: {e}")
            continue
        results.append(r)
        print(f"{r['method']:<10} {r['backend']:<8} {r['dim']:>5} "
              f"{r['top1']:>7.1%} {r['top5']:>7.1%} {r['embed_ms']:>9.1f} "
              f"{r['embed_ms_p95']:>8.1f} {r['search_ms']:>10.2f}")

    print(f"\n({len(queries)} requêtes sur {len(references)} cartes ; "
          f"critère F01 : top-1 ≥ 90 %, latence < 50 ms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
