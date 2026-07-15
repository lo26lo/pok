#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_card_index.py — F01 : construction de l'index d'identification de cartes
===============================================================================

Construit l'index d'embeddings (models/card_index/) à partir des images
TCGdex téléchargées (images/), pour l'identification fine des cartes après
détection YOLO (core/card_identifier.py).

Usage :
    python tools/build_card_index.py                          # défauts
    python tools/build_card_index.py --images images --method auto
    python tools/build_card_index.py --download-model         # récupère l'ONNX

Méthodes :
    auto     dnn si le modèle ONNX est présent, sinon classic (défaut)
    dnn      MobileNetV2 via cv2.dnn — recommandé (voir benchmark F01)
    classic  descripteur couleur+gradients pur OpenCV — aucun fichier requis

Vérification rapide de l'index après construction :
    python tools/build_card_index.py --check
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.card_identifier import (  # noqa: E402
    CardIndex, DEFAULT_INDEX_DIR, DEFAULT_ONNX_PATH, EMBEDDING_MODEL_URL,
    EMBEDDING_MODEL_POOL_OUTPUT,
)
from core.utils import PATHS, safe_print  # noqa: E402


def download_model(dest: str = None) -> bool:
    """
    Télécharge le modèle ONNX MobileNetV2 pour la méthode dnn, puis le
    tronque à la couche global-pool (features 1280-d, nettement plus
    discriminantes que les logits — cf. benchmark F01) si le package
    ``onnx`` est installé. Sans troncature le modèle complet reste
    utilisable (logits 1000-d).
    """
    import requests

    dest = Path(dest or DEFAULT_ONNX_PATH)
    if dest.exists():
        safe_print(f"✅ Modèle déjà présent: {dest}")
        return True
    safe_print(f"⬇️  Téléchargement du modèle ONNX...\n    {EMBEDDING_MODEL_URL}")
    try:
        r = requests.get(EMBEDDING_MODEL_URL, timeout=120)
        r.raise_for_status()
    except Exception as e:
        safe_print(f"❌ Téléchargement impossible: {e}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(r.content)
    safe_print(f"✅ Modèle sauvegardé: {dest} ({len(r.content) / 1e6:.1f} Mo)")

    try:
        import onnx
        full = dest.with_suffix('.full.onnx')
        dest.rename(full)
        onnx.utils.extract_model(str(full), str(dest), ['data'],
                                 [EMBEDDING_MODEL_POOL_OUTPUT],
                                 check_model=False)
        full.unlink()
        safe_print("✂️  Modèle tronqué à la couche global-pool (features 1280-d)")
    except ImportError:
        safe_print("ℹ️  Package 'onnx' absent: modèle complet conservé "
                   "(logits 1000-d, précision moindre — pip install onnx "
                   "puis relancez pour la version 1280-d)")
    except Exception as e:
        safe_print(f"⚠️ Troncature impossible ({e}) — modèle complet conservé")
        full = dest.with_suffix('.full.onnx')
        if full.exists() and not dest.exists():
            full.rename(dest)
    return True


def check_index(index_dir: str = None) -> int:
    """Affiche l'état de l'index existant."""
    try:
        index = CardIndex.load(index_dir)
    except FileNotFoundError as e:
        safe_print(f"❌ {e}")
        return 1
    meta = index.meta
    safe_print(f"✅ Index: {meta['count']} cartes, méthode '{meta['method']}' "
               f"(dim={meta['dim']}), backend {index.backend}")
    safe_print(f"   Construit le {meta.get('built_at', '?')} "
               f"depuis {meta.get('built_from', '?')}")
    sets = sorted({c['set_id'] for c in index.cards})
    safe_print(f"   Sets indexés: {', '.join(sets)}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Construction de l'index d'identification de cartes (F01)"
    )
    parser.add_argument("--images", default=PATHS['directories']['images'],
                        help="Dossier des images TCGdex (défaut: images/)")
    parser.add_argument("--out", default=DEFAULT_INDEX_DIR,
                        help=f"Dossier de sortie (défaut: {DEFAULT_INDEX_DIR})")
    parser.add_argument("--method", default="auto",
                        choices=["auto", "classic", "dnn"],
                        help="Embedder (défaut: auto)")
    parser.add_argument("--model", default=None,
                        help="Chemin du modèle ONNX (méthode dnn)")
    parser.add_argument("--download-model", action="store_true",
                        help="Télécharge le modèle ONNX MobileNetV2 puis continue")
    parser.add_argument("--check", action="store_true",
                        help="Affiche l'état de l'index existant et quitte")
    args = parser.parse_args()

    if args.check:
        return check_index(args.out)

    if args.download_model:
        if not download_model(args.model):
            return 1

    try:
        index = CardIndex.build(args.images, method=args.method,
                                model_path=args.model)
    except (FileNotFoundError, ValueError) as e:
        safe_print(f"❌ {e}")
        return 1

    out_dir = index.save(args.out)
    safe_print(f"💾 Index sauvegardé dans {out_dir}/ "
               f"({index.meta['count']} cartes, méthode '{index.meta['method']}')")
    safe_print("   Activez « Identify Cards » dans la vue Detection de la GUI "
               "pour l'utiliser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
