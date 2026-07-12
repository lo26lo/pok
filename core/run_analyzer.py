#!/usr/bin/env python3
"""
Analyse des runs d'entraînement YOLO (F07 - onglet Évaluation)

Fonctions pures et testables pour :
- lister les runs de runs/train/ et parser leurs artefacts Ultralytics
  (results.csv, args.yaml, courbes PNG déjà générées) ;
- résumer un run (meilleures métriques, hyperparamètres) et comparer
  deux runs (deltas) ;
- classer les « pires prédictions » : score d'erreur par image
  (cartes manquées, faux positifs, mauvaises classes) et planche contact
  annotée (vérité terrain en vert, prédictions en rouge).

L'inférence (rank_worst_images) nécessite ultralytics ; tout le reste est
sans dépendance lourde.
"""
import csv
import os
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

try:
    from .utils import PATHS, safe_print
except ImportError:
    from utils import PATHS, safe_print

RUNS_DIR = PATHS['directories'].get('runs_train', 'runs/train')
REAL_VAL_REPORT = os.path.join(PATHS['directories'].get('output_base', 'output'),
                               "real_val_report.json")

# Artefacts PNG produits par Ultralytics, dans l'ordre d'affichage GUI
KNOWN_PLOTS = [
    ("results", "results.png"),
    ("confusion_matrix", "confusion_matrix.png"),
    ("confusion_matrix_normalized", "confusion_matrix_normalized.png"),
    ("PR_curve", "PR_curve.png"),
    ("F1_curve", "F1_curve.png"),
    ("P_curve", "P_curve.png"),
    ("R_curve", "R_curve.png"),
    ("labels", "labels.jpg"),
]

# Clés de métriques (colonnes results.csv Ultralytics, espaces déjà strippés)
METRIC_KEYS = {
    "precision": "metrics/precision(B)",
    "recall": "metrics/recall(B)",
    "mAP50": "metrics/mAP50(B)",
    "mAP50-95": "metrics/mAP50-95(B)",
}


# ---------------------------------------------------------------- Runs

def list_runs(runs_dir: str = RUNS_DIR) -> List[Dict]:
    """
    Liste les runs d'entraînement (dossiers contenant results.csv ou
    weights/), triés du plus récent au plus ancien.
    """
    runs = []
    if not os.path.isdir(runs_dir):
        return runs
    for entry in sorted(os.listdir(runs_dir)):
        path = os.path.join(runs_dir, entry)
        if not os.path.isdir(path):
            continue
        has_results = os.path.exists(os.path.join(path, "results.csv"))
        has_weights = os.path.exists(os.path.join(path, "weights", "best.pt"))
        if not (has_results or has_weights):
            continue
        runs.append({
            "name": entry,
            "path": path,
            "has_results": has_results,
            "has_weights": has_weights,
            "mtime": os.path.getmtime(path),
        })
    runs.sort(key=lambda r: r["mtime"], reverse=True)
    return runs


def parse_results_csv(csv_path: str) -> Dict[str, List[float]]:
    """
    Parse un results.csv Ultralytics en colonnes {nom: [valeurs]}.
    Les noms de colonnes sont strippés (Ultralytics les padde d'espaces).
    """
    columns: Dict[str, List[float]] = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for raw_key, value in row.items():
                if raw_key is None or value is None:
                    continue
                key = raw_key.strip()
                try:
                    columns.setdefault(key, []).append(float(value.strip()))
                except ValueError:
                    continue
    return columns


def run_summary(run_path: str) -> Dict:
    """
    Résumé d'un run : meilleures métriques (au meilleur epoch mAP50-95),
    nombre d'epochs effectués, hyperparamètres clés (args.yaml),
    real_mAP si le rapport F08 mentionne le best.pt de ce run.
    """
    summary: Dict = {"name": os.path.basename(run_path.rstrip("/\\")),
                     "path": run_path, "metrics": {}, "args": {}}

    csv_path = os.path.join(run_path, "results.csv")
    if os.path.exists(csv_path):
        cols = parse_results_csv(csv_path)
        epochs = cols.get("epoch", [])
        summary["epochs_done"] = len(epochs)
        map_col = cols.get(METRIC_KEYS["mAP50-95"], [])
        if map_col:
            best_idx = int(np.argmax(map_col))
            summary["best_epoch"] = int(epochs[best_idx]) if epochs else best_idx
            for short, col_name in METRIC_KEYS.items():
                values = cols.get(col_name, [])
                if values:
                    summary["metrics"][short] = round(values[best_idx], 4)

    args_path = os.path.join(run_path, "args.yaml")
    if os.path.exists(args_path):
        try:
            import yaml
            with open(args_path, 'r', encoding='utf-8') as f:
                args = yaml.safe_load(f) or {}
            summary["args"] = {k: args.get(k) for k in
                               ("model", "data", "epochs", "batch", "imgsz",
                                "optimizer", "lr0") if k in args}
        except Exception:
            pass

    best_pt = os.path.join(run_path, "weights", "best.pt")
    summary["best_model"] = best_pt if os.path.exists(best_pt) else None

    real = load_real_val_history()
    if real and summary["best_model"]:
        best_abs = os.path.abspath(summary["best_model"])
        matching = [h for h in real
                    if os.path.abspath(h.get("model", "")) == best_abs]
        if matching:
            summary["metrics"]["real_mAP50"] = round(
                matching[-1]["real_mAP50"], 4)

    return summary


def compare_runs(summary_a: Dict, summary_b: Dict) -> Dict[str, float]:
    """Deltas (B - A) des métriques communes aux deux runs."""
    deltas = {}
    for key in summary_a.get("metrics", {}):
        if key in summary_b.get("metrics", {}):
            deltas[key] = round(summary_b["metrics"][key]
                                - summary_a["metrics"][key], 4)
    return deltas


def available_plots(run_path: str) -> Dict[str, str]:
    """Artefacts PNG existants du run {nom: chemin}, ordre d'affichage."""
    plots = {}
    for name, filename in KNOWN_PLOTS:
        path = os.path.join(run_path, filename)
        if os.path.exists(path):
            plots[name] = path
    # Aperçus de validation (prédictions du dernier epoch)
    for pred in sorted(glob(os.path.join(run_path, "val_batch*_pred.jpg")))[:3]:
        plots[os.path.splitext(os.path.basename(pred))[0]] = pred
    return plots


def load_real_val_history(report_path: str = REAL_VAL_REPORT) -> List[Dict]:
    """Historique real_mAP du rapport F08 ([] si absent/corrompu)."""
    import json
    if not os.path.exists(report_path):
        return []
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f).get("history", [])
    except (OSError, ValueError):
        return []


# ------------------------------------------------- Pires prédictions

def iou_xywh(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    """IoU de deux boîtes (cx, cy, w, h) normalisées ou en pixels."""
    ax0, ay0 = box_a[0] - box_a[2] / 2, box_a[1] - box_a[3] / 2
    ax1, ay1 = box_a[0] + box_a[2] / 2, box_a[1] + box_a[3] / 2
    bx0, by0 = box_b[0] - box_b[2] / 2, box_b[1] - box_b[3] / 2
    bx1, by1 = box_b[0] + box_b[2] / 2, box_b[1] + box_b[3] / 2

    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    union = box_a[2] * box_a[3] + box_b[2] * box_b[3] - inter
    return float(inter / union) if union > 0 else 0.0


def score_image_errors(gt_boxes: List[Tuple], pred_boxes: List[Tuple],
                       iou_threshold: float = 0.5) -> Dict:
    """
    Score d'erreur d'une image : appariement glouton GT/prédictions par
    IoU décroissante, puis comptage des cartes manquées, faux positifs
    et erreurs de classe. Boîtes: (class_id, cx, cy, w, h[, conf]).
    score = misses + false_positives + wrong_class (plus haut = pire).
    """
    pairs = []
    for gi, gt in enumerate(gt_boxes):
        for pi, pred in enumerate(pred_boxes):
            iou = iou_xywh(gt[1:5], pred[1:5])
            if iou >= iou_threshold:
                pairs.append((iou, gi, pi))
    pairs.sort(reverse=True)

    matched_gt, matched_pred = set(), set()
    wrong_class = 0
    for iou, gi, pi in pairs:
        if gi in matched_gt or pi in matched_pred:
            continue
        matched_gt.add(gi)
        matched_pred.add(pi)
        if int(gt_boxes[gi][0]) != int(pred_boxes[pi][0]):
            wrong_class += 1

    misses = len(gt_boxes) - len(matched_gt)
    false_positives = len(pred_boxes) - len(matched_pred)
    return {
        "misses": misses,
        "false_positives": false_positives,
        "wrong_class": wrong_class,
        "matched": len(matched_gt),
        "score": misses + false_positives + wrong_class,
    }


def read_yolo_labels(label_path: str) -> List[Tuple]:
    """Lit un fichier YOLO en [(class_id, cx, cy, w, h), ...] ([] si absent)."""
    boxes = []
    if not os.path.exists(label_path):
        return boxes
    with open(label_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 5:
                try:
                    boxes.append((int(parts[0]), *map(float, parts[1:5])))
                except ValueError:
                    continue
    return boxes


def draw_error_overlay(image: np.ndarray, gt_boxes: List[Tuple],
                       pred_boxes: List[Tuple]) -> np.ndarray:
    """Dessine la vérité terrain (vert) et les prédictions (rouge)."""
    out = image.copy()
    h, w = out.shape[:2]
    for cls, cx, cy, bw, bh, *_ in gt_boxes:
        x0, y0 = int((cx - bw / 2) * w), int((cy - bh / 2) * h)
        x1, y1 = int((cx + bw / 2) * w), int((cy + bh / 2) * h)
        cv2.rectangle(out, (x0, y0), (x1, y1), (80, 220, 80), 2)
    for cls, cx, cy, bw, bh, *_ in pred_boxes:
        x0, y0 = int((cx - bw / 2) * w), int((cy - bh / 2) * h)
        x1, y1 = int((cx + bw / 2) * w), int((cy + bh / 2) * h)
        cv2.rectangle(out, (x0, y0), (x1, y1), (60, 60, 230), 2)
    return out


def rank_worst_images(model_path: str, image_paths: List[str],
                      labels_dir: str, top_k: int = 8, conf: float = 0.25,
                      device: str = "cpu",
                      log=safe_print) -> Optional[List[Dict]]:
    """
    Classe les images par score d'erreur décroissant (pires en premier).
    Retourne [{image, score, misses, false_positives, wrong_class,
    gt_boxes, pred_boxes}, ...] ou None si ultralytics est absent.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        log("ℹ️ ultralytics non installé — classement des pires prédictions indisponible")
        return None

    model = YOLO(str(model_path))
    ranked = []
    for img_path in image_paths:
        stem = Path(img_path).stem
        gt = read_yolo_labels(os.path.join(labels_dir, f"{stem}.txt"))
        results = model.predict(img_path, conf=conf, device=device,
                                verbose=False)
        preds = []
        for box in results[0].boxes:
            cx, cy, bw, bh = box.xywhn[0].tolist()
            preds.append((int(box.cls.item()), cx, cy, bw, bh,
                          float(box.conf.item())))
        errors = score_image_errors(gt, preds)
        ranked.append({"image": img_path, "gt_boxes": gt,
                       "pred_boxes": preds, **errors})

    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:top_k]


def build_worst_sheet(ranked: List[Dict], cols: int = 4,
                      thumb_size: Tuple[int, int] = (320, 240)) -> np.ndarray:
    """
    Planche contact des pires prédictions : vignettes annotées
    (GT vert / prédictions rouge) + score d'erreur en légende.
    """
    tw, th = thumb_size
    rows = max(1, (len(ranked) + cols - 1) // cols)
    sheet = np.full((rows * th, cols * tw, 3), 30, np.uint8)

    for idx, item in enumerate(ranked):
        img = cv2.imread(item["image"], cv2.IMREAD_COLOR)
        if img is None:
            continue
        annotated = draw_error_overlay(img, item["gt_boxes"],
                                       item["pred_boxes"])
        thumb = cv2.resize(annotated, (tw, th), interpolation=cv2.INTER_AREA)
        caption = (f"err {item['score']} (M{item['misses']} "
                   f"FP{item['false_positives']} C{item['wrong_class']})")
        cv2.rectangle(thumb, (0, th - 24), (tw, th), (20, 20, 20), -1)
        cv2.putText(thumb, caption, (6, th - 7), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1, cv2.LINE_AA)
        r, c = divmod(idx, cols)
        sheet[r * th:(r + 1) * th, c * tw:(c + 1) * tw] = thumb
    return sheet


def resolve_eval_source() -> Optional[Dict]:
    """
    Source d'images pour le classement des pires prédictions :
    1) le set réel F08 s'il est prêt (le plus pertinent),
    2) sinon le split val du dataset fusionné (val.txt).
    Retourne {'label', 'images': [...], 'labels_dir'} ou None.
    """
    try:
        from .real_validation import check_real_val_set, DEFAULT_REAL_VAL_DIR, list_images
    except ImportError:
        from real_validation import check_real_val_set, DEFAULT_REAL_VAL_DIR, list_images

    status = check_real_val_set(DEFAULT_REAL_VAL_DIR)
    if status["ready"]:
        return {
            "label": "set réel (datasets/real_val)",
            "images": list_images(os.path.join(DEFAULT_REAL_VAL_DIR, "images")),
            "labels_dir": os.path.join(DEFAULT_REAL_VAL_DIR, "labels"),
        }

    merged = PATHS['directories'].get('output_dataset_merged',
                                      'output/dataset_merged')
    val_txt = os.path.join(merged, "val.txt")
    labels_dir = os.path.join(merged, "labels")
    if os.path.exists(val_txt) and os.path.isdir(labels_dir):
        with open(val_txt, 'r', encoding='utf-8') as f:
            images = [line.strip() for line in f if line.strip()]
        images = [p for p in images if os.path.exists(p)]
        if images:
            return {"label": "val synthétique (dataset_merged)",
                    "images": images, "labels_dir": labels_dir}
    return None
