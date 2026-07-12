"""
Tests de l'analyse des runs d'entraînement (F07).

Couvre le parsing des artefacts Ultralytics (results.csv, args.yaml,
PNGs), les résumés/comparaisons, le score d'erreur des pires prédictions
(IoU, appariement, comptages) et les helpers purs de la vue GUI.
L'inférence (rank_worst_images) nécessite ultralytics — hors périmètre.
"""
import numpy as np
import pytest

from core.run_analyzer import (
    available_plots,
    build_worst_sheet,
    compare_runs,
    draw_error_overlay,
    iou_xywh,
    list_runs,
    parse_results_csv,
    read_yolo_labels,
    run_summary,
    score_image_errors,
)

RESULTS_CSV = """epoch,      train/box_loss,      metrics/precision(B),      metrics/recall(B),      metrics/mAP50(B),      metrics/mAP50-95(B)
0,          1.5,                 0.40,                      0.35,                   0.30,                  0.20
1,          1.2,                 0.60,                      0.55,                   0.58,                  0.45
2,          1.0,                 0.55,                      0.50,                   0.52,                  0.40
"""


@pytest.fixture
def fake_run(tmp_path):
    """Run Ultralytics factice : results.csv, args.yaml, PNGs, best.pt."""
    cv2 = pytest.importorskip("cv2")
    run = tmp_path / "runs" / "train" / "pokemon_detector"
    (run / "weights").mkdir(parents=True)
    (run / "results.csv").write_text(RESULTS_CSV, encoding="utf-8")
    (run / "args.yaml").write_text(
        "model: yolov8n.pt\ndata: data.yaml\nepochs: 3\nbatch: 16\nimgsz: 640\n",
        encoding="utf-8")
    (run / "weights" / "best.pt").write_bytes(b"fake")
    img = np.zeros((40, 60, 3), np.uint8)
    for name in ["results.png", "confusion_matrix.png", "PR_curve.png",
                 "val_batch0_pred.jpg"]:
        cv2.imwrite(str(run / name), img)
    return run


class TestRunParsing:
    def test_parse_results_csv_strips_columns(self, fake_run):
        cols = parse_results_csv(str(fake_run / "results.csv"))
        assert cols["epoch"] == [0.0, 1.0, 2.0]
        assert cols["metrics/mAP50(B)"] == [0.30, 0.58, 0.52]

    def test_list_runs(self, fake_run):
        runs = list_runs(str(fake_run.parent))
        assert len(runs) == 1
        assert runs[0]["name"] == "pokemon_detector"
        assert runs[0]["has_results"] and runs[0]["has_weights"]

    def test_list_runs_missing_dir(self, tmp_path):
        assert list_runs(str(tmp_path / "nope")) == []

    def test_run_summary_best_epoch(self, fake_run):
        summary = run_summary(str(fake_run))
        # meilleur epoch = mAP50-95 max = epoch 1
        assert summary["best_epoch"] == 1
        assert summary["epochs_done"] == 3
        assert summary["metrics"]["mAP50"] == 0.58
        assert summary["metrics"]["mAP50-95"] == 0.45
        assert summary["args"]["model"] == "yolov8n.pt"
        assert summary["best_model"].endswith("best.pt")

    def test_compare_runs_deltas(self, fake_run):
        a = run_summary(str(fake_run))
        b = {"metrics": {"mAP50": 0.68, "mAP50-95": 0.50}}
        deltas = compare_runs(a, b)
        assert deltas["mAP50"] == pytest.approx(0.10, abs=1e-6)
        assert deltas["mAP50-95"] == pytest.approx(0.05, abs=1e-6)
        assert "precision" not in deltas  # absent du run B

    def test_available_plots_order_and_presence(self, fake_run):
        plots = available_plots(str(fake_run))
        assert list(plots)[:3] == ["results", "confusion_matrix", "PR_curve"]
        assert "val_batch0_pred" in plots


class TestErrorScoring:
    def test_iou_identical_and_disjoint(self):
        box = (0.5, 0.5, 0.2, 0.2)
        assert iou_xywh(box, box) == pytest.approx(1.0)
        assert iou_xywh(box, (0.9, 0.9, 0.1, 0.1)) == 0.0

    def test_iou_partial(self):
        # Deux boîtes 0.2x0.2 décalées de la moitié : inter=0.1*0.2
        a = (0.5, 0.5, 0.2, 0.2)
        b = (0.6, 0.5, 0.2, 0.2)
        assert iou_xywh(a, b) == pytest.approx(0.02 / 0.06, abs=1e-6)

    def test_perfect_prediction(self):
        gt = [(0, 0.5, 0.5, 0.2, 0.2)]
        pred = [(0, 0.5, 0.5, 0.2, 0.2, 0.9)]
        s = score_image_errors(gt, pred)
        assert s["score"] == 0 and s["matched"] == 1

    def test_missed_card(self):
        gt = [(0, 0.5, 0.5, 0.2, 0.2), (1, 0.2, 0.2, 0.1, 0.1)]
        pred = [(0, 0.5, 0.5, 0.2, 0.2, 0.9)]
        s = score_image_errors(gt, pred)
        assert s["misses"] == 1 and s["false_positives"] == 0
        assert s["score"] == 1

    def test_false_positive(self):
        gt = []
        pred = [(0, 0.5, 0.5, 0.2, 0.2, 0.9)]
        s = score_image_errors(gt, pred)
        assert s["false_positives"] == 1 and s["score"] == 1

    def test_wrong_class_counts(self):
        gt = [(0, 0.5, 0.5, 0.2, 0.2)]
        pred = [(3, 0.5, 0.5, 0.2, 0.2, 0.9)]
        s = score_image_errors(gt, pred)
        assert s["wrong_class"] == 1 and s["misses"] == 0
        assert s["score"] == 1

    def test_greedy_matching_prefers_best_iou(self):
        gt = [(0, 0.5, 0.5, 0.2, 0.2)]
        pred = [(0, 0.52, 0.5, 0.2, 0.2, 0.9),   # bon recouvrement
                (0, 0.58, 0.5, 0.2, 0.2, 0.9)]   # recouvrement plus faible
        s = score_image_errors(gt, pred)
        assert s["matched"] == 1
        assert s["false_positives"] == 1


class TestGalleryHelpers:
    def test_read_yolo_labels(self, tmp_path):
        p = tmp_path / "img.txt"
        p.write_text("2 0.5 0.5 0.2 0.3\ninvalide\n", encoding="utf-8")
        boxes = read_yolo_labels(str(p))
        assert boxes == [(2, 0.5, 0.5, 0.2, 0.3)]
        assert read_yolo_labels(str(tmp_path / "absent.txt")) == []

    def test_draw_error_overlay_modifies_box_regions(self):
        img = np.zeros((100, 100, 3), np.uint8)
        out = draw_error_overlay(img, [(0, 0.5, 0.5, 0.4, 0.4)],
                                 [(0, 0.3, 0.3, 0.2, 0.2)])
        assert out.shape == img.shape
        assert out.sum() > 0
        assert img.sum() == 0  # l'original n'est pas modifié

    def test_build_worst_sheet(self, tmp_path):
        cv2 = pytest.importorskip("cv2")
        img_path = tmp_path / "photo.jpg"
        cv2.imwrite(str(img_path), np.full((120, 160, 3), 90, np.uint8))
        ranked = [{
            "image": str(img_path), "score": 2, "misses": 1,
            "false_positives": 1, "wrong_class": 0,
            "gt_boxes": [(0, 0.5, 0.5, 0.4, 0.4)],
            "pred_boxes": [(0, 0.2, 0.2, 0.2, 0.2, 0.8)],
        }]
        sheet = build_worst_sheet(ranked, cols=4, thumb_size=(160, 120))
        assert sheet.shape == (120, 640, 3)


class TestViewHelpers:
    """Helpers purs de gui/evaluation_view.py (sans Tk)."""

    def test_load_image_fit_downscales(self, tmp_path):
        cv2 = pytest.importorskip("cv2")
        import base64
        from gui.evaluation_view import load_image_fit
        big = tmp_path / "big.png"
        cv2.imwrite(str(big), np.zeros((1200, 2000, 3), np.uint8))
        data = load_image_fit(str(big), max_w=800, max_h=500)
        raw = base64.b64decode(data)
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        assert load_image_fit(str(tmp_path / "absent.png")) is None

    def test_format_summary(self, fake_run):
        from gui.evaluation_view import format_summary
        text = format_summary(run_summary(str(fake_run)))
        assert "pokemon_detector" in text
        assert "mAP50: 0.580" in text
        assert "model=yolov8n.pt" in text

    def test_format_comparison(self):
        from gui.evaluation_view import format_comparison
        a = {"name": "runA", "metrics": {"mAP50": 0.5}}
        b = {"name": "runB", "metrics": {"mAP50": 0.6}}
        text = format_comparison(a, b, compare_runs(a, b))
        assert "runB" in text and "▲" in text and "+0.100" in text
        assert format_comparison(a, b, {}) == "Aucune métrique commune."
