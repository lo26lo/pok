#!/usr/bin/env python3
"""
Évaluation sur set de validation RÉEL (F08)

Le dataset d'entraînement est 100 % synthétique (mosaïques générées).
Ce module mesure le VRAI transfert au monde réel : un petit set de photos
de vraies cartes, annoté à la main, jamais vu à l'entraînement, évalué
séparément (métrique `real_mAP`).

Structure attendue (voir datasets/real_val/README.md pour le protocole) :
    datasets/real_val/
    ├── images/   *.jpg / *.png  (photos réelles)
    └── labels/   *.txt          (annotations YOLO, 1 fichier par image)

Garanties :
- le set réel n'entre JAMAIS dans le train : garde anti-fuite par hash MD5
  contre les dossiers d'entraînement ;
- l'évaluation est automatique en fin d'entraînement si le set existe
  (TrainingManager), et disponible en CLI :
      python core/real_validation.py --model runs/train/pokemon_detector/weights/best.pt
"""
import argparse
import hashlib
import json
import os
import sys
import time
from glob import glob
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

try:
    from .utils import safe_print, PATHS
except ImportError:
    from utils import safe_print, PATHS

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

DEFAULT_REAL_VAL_DIR = "datasets/real_val"
DEFAULT_REPORT_PATH = os.path.join(PATHS['directories'].get('output_base', 'output'),
                                   "real_val_report.json")

# Dossiers d'entraînement à contrôler pour la garde anti-fuite
DEFAULT_TRAIN_DIRS = [
    PATHS['directories'].get('output_dataset_images', 'output/dataset/images'),
    PATHS['directories'].get('output_augmented_images', 'output/augmented/images'),
    PATHS['directories'].get('output_mosaics_images', 'output/mosaics/images'),
    os.path.join(PATHS['directories'].get('output_dataset_merged',
                                          'output/dataset_merged'), 'images'),
]


def list_images(directory: str) -> List[str]:
    """Liste triée des images d'un dossier (extensions usuelles)."""
    paths = []
    for ext in IMAGE_EXTENSIONS:
        paths.extend(glob(os.path.join(directory, f"*{ext}")))
        paths.extend(glob(os.path.join(directory, f"*{ext.upper()}")))
    return sorted(set(paths))


def validate_label_file(label_path: str,
                        num_classes: Optional[int] = None) -> List[str]:
    """
    Vérifie un fichier d'annotation YOLO. Retourne la liste des erreurs
    ([] = valide). Un fichier vide est valide (image sans carte).
    """
    errors = []
    try:
        with open(label_path, 'r', encoding='utf-8') as f:
            lines = f.read().strip().splitlines()
    except OSError as e:
        return [f"illisible: {e}"]

    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"ligne {idx}: {len(parts)} champs (5 attendus)")
            continue
        try:
            cls = int(parts[0])
            cx, cy, w, h = map(float, parts[1:])
        except ValueError:
            errors.append(f"ligne {idx}: valeurs non numériques")
            continue
        if cls < 0 or (num_classes is not None and cls >= num_classes):
            errors.append(f"ligne {idx}: class_id {cls} hors plage")
        if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 < w <= 1 and 0 < h <= 1):
            errors.append(f"ligne {idx}: coordonnées hors [0,1]")
        elif cx - w / 2 < -0.01 or cx + w / 2 > 1.01 or \
                cy - h / 2 < -0.01 or cy + h / 2 > 1.01:
            errors.append(f"ligne {idx}: bbox déborde de l'image")
    return errors


def check_real_val_set(root: str = DEFAULT_REAL_VAL_DIR,
                       num_classes: Optional[int] = None) -> Dict:
    """
    État du set réel : nombre d'images, annotées ou non, erreurs de labels.
    `ready` = au moins 1 image annotée et aucun label invalide.
    """
    images_dir = os.path.join(root, "images")
    labels_dir = os.path.join(root, "labels")
    images = list_images(images_dir)

    labeled, unlabeled, invalid = [], [], {}
    for img in images:
        stem = Path(img).stem
        label = os.path.join(labels_dir, f"{stem}.txt")
        if not os.path.exists(label):
            unlabeled.append(os.path.basename(img))
            continue
        errors = validate_label_file(label, num_classes)
        if errors:
            invalid[os.path.basename(label)] = errors
        else:
            labeled.append(os.path.basename(img))

    return {
        "root": root,
        "total_images": len(images),
        "labeled": len(labeled),
        "unlabeled_files": unlabeled,
        "invalid_labels": invalid,
        "ready": len(labeled) > 0 and not invalid,
    }


def _md5(path: str, chunk_size: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def find_train_leakage(real_root: str = DEFAULT_REAL_VAL_DIR,
                       train_dirs: Optional[List[str]] = None
                       ) -> List[Tuple[str, str]]:
    """
    Garde anti-fuite : détecte les images du set réel présentes à
    l'identique (hash MD5) dans les dossiers d'entraînement.
    Retourne [(image_réelle, image_train), ...] — vide = aucun leak.
    """
    if train_dirs is None:
        train_dirs = DEFAULT_TRAIN_DIRS

    real_images = list_images(os.path.join(real_root, "images"))
    if not real_images:
        return []
    real_hashes = {_md5(p): p for p in real_images}

    leaks = []
    for train_dir in train_dirs:
        if not os.path.isdir(train_dir):
            continue
        for train_img in list_images(train_dir):
            h = _md5(train_img)
            if h in real_hashes:
                leaks.append((real_hashes[h], train_img))
    return leaks


def build_val_data_yaml(real_root: str, class_names: List[str],
                        out_path: Optional[str] = None) -> str:
    """
    Écrit le data.yaml pointant la validation sur le set réel.
    (train pointe aussi sur le set réel : exigé par le format Ultralytics,
    mais jamais utilisé en mode val.)
    """
    import yaml
    root_abs = os.path.abspath(real_root)
    data = {
        "path": root_abs,
        "train": "images",
        "val": "images",
        "nc": len(class_names),
        "names": list(class_names),
    }
    if out_path is None:
        out_path = os.path.join(real_root, "data_real_val.yaml")
    with open(out_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    return out_path


def evaluate_real_map(model_path: str,
                      real_root: str = DEFAULT_REAL_VAL_DIR,
                      device: str = "cpu",
                      report_path: str = DEFAULT_REPORT_PATH,
                      log: Callable[[str], None] = safe_print) -> Optional[Dict]:
    """
    Évalue un modèle YOLO sur le set réel et retourne les métriques
    {'real_mAP50', 'real_mAP50_95', 'real_precision', 'real_recall', ...}.
    Écrit un rapport JSON (avec historique des runs) dans report_path.
    Retourne None si le set n'est pas prêt ou si ultralytics est absent.
    """
    status = check_real_val_set(real_root)
    if not status["ready"]:
        if status["total_images"] == 0:
            log(f"ℹ️ Set réel vide ({real_root}) — évaluation real_mAP sautée")
        else:
            log(f"⚠️ Set réel non prêt: {status['labeled']} annotées / "
                f"{status['total_images']} images, "
                f"{len(status['invalid_labels'])} labels invalides")
        return None

    leaks = find_train_leakage(real_root)
    if leaks:
        log(f"❌ FUITE DÉTECTÉE: {len(leaks)} image(s) du set réel sont "
            f"dans les données d'entraînement — évaluation refusée")
        for real_img, train_img in leaks[:5]:
            log(f"   {os.path.basename(real_img)} == {train_img}")
        return None

    try:
        from ultralytics import YOLO
    except ImportError:
        log("ℹ️ ultralytics non installé — évaluation real_mAP sautée")
        return None

    log(f"🌍 Évaluation sur le set RÉEL ({status['labeled']} images annotées)…")
    model = YOLO(str(model_path))
    class_names = [model.names[k] for k in sorted(model.names)]
    data_yaml = build_val_data_yaml(real_root, class_names)

    results = model.val(data=data_yaml, device=device, verbose=False,
                        plots=False)
    metrics = {
        "real_mAP50": float(results.box.map50),
        "real_mAP50_95": float(results.box.map),
        "real_precision": float(results.box.mp),
        "real_recall": float(results.box.mr),
        "images": status["labeled"],
        "model": str(model_path),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    log(f"   real_mAP50    : {metrics['real_mAP50']:.3f}")
    log(f"   real_mAP50-95 : {metrics['real_mAP50_95']:.3f}")
    log(f"   real_precision: {metrics['real_precision']:.3f}")
    log(f"   real_recall   : {metrics['real_recall']:.3f}")

    save_report(metrics, report_path)
    log(f"📄 Rapport: {report_path}")
    return metrics


def save_report(metrics: Dict, report_path: str = DEFAULT_REPORT_PATH) -> None:
    """Ajoute le run à l'historique JSON (dernier run + liste complète)."""
    os.makedirs(os.path.dirname(report_path) or ".", exist_ok=True)
    history = []
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                history = json.load(f).get("history", [])
        except (OSError, json.JSONDecodeError):
            history = []
    history.append(metrics)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({"latest": metrics, "history": history}, f,
                  ensure_ascii=False, indent=2)


def auto_evaluate_if_available(model_path,
                               log: Callable[[str], None] = safe_print,
                               real_root: str = DEFAULT_REAL_VAL_DIR,
                               device: str = "cpu") -> Optional[Dict]:
    """
    Point d'entrée pour la fin d'entraînement (TrainingManager) :
    évalue sur le set réel s'il est prêt, sans jamais faire échouer
    l'entraînement (toute erreur est loguée puis avalée).
    """
    try:
        return evaluate_real_map(str(model_path), real_root=real_root,
                                 device=device, log=log)
    except Exception as e:
        log(f"⚠️ Évaluation real_mAP échouée (non bloquant): {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Évaluation d'un modèle YOLO sur le set de validation réel")
    parser.add_argument("--model",
                        default=PATHS['files'].get(
                            'best_model',
                            'runs/train/pokemon_detector/weights/best.pt'),
                        help="Chemin du modèle .pt")
    parser.add_argument("--dir", default=DEFAULT_REAL_VAL_DIR,
                        help="Racine du set réel")
    parser.add_argument("--device", default="cpu", help="cpu, 0, 0,1…")
    parser.add_argument("--report", default=DEFAULT_REPORT_PATH,
                        help="Chemin du rapport JSON")
    parser.add_argument("--check", action="store_true",
                        help="Vérifier seulement l'état du set (pas d'évaluation)")
    args = parser.parse_args()

    status = check_real_val_set(args.dir)
    safe_print(f"📂 Set réel: {status['root']}")
    safe_print(f"   Images: {status['total_images']} "
               f"({status['labeled']} annotées)")
    if status["unlabeled_files"]:
        safe_print(f"   ⚠️ Sans label: {len(status['unlabeled_files'])} "
                   f"(ex: {status['unlabeled_files'][:3]})")
    for name, errors in status["invalid_labels"].items():
        safe_print(f"   ❌ {name}: {'; '.join(errors[:3])}")

    leaks = find_train_leakage(args.dir)
    if leaks:
        safe_print(f"   ❌ FUITE: {len(leaks)} image(s) aussi dans le train!")
    else:
        safe_print("   ✅ Aucune fuite vers les données d'entraînement")

    if args.check:
        sys.exit(0 if status["ready"] and not leaks else 1)

    if not os.path.exists(args.model):
        safe_print(f"❌ Modèle introuvable: {args.model}")
        sys.exit(1)

    metrics = evaluate_real_map(args.model, real_root=args.dir,
                                device=args.device, report_path=args.report)
    sys.exit(0 if metrics else 1)


if __name__ == "__main__":
    main()
