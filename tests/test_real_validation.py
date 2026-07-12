"""
Tests du set de validation réel (F08).

Couvre les parties pures : validation des labels YOLO, état du set,
garde anti-fuite MD5, data.yaml, rapport JSON, et le contrat de
auto_evaluate_if_available (ne lève jamais). L'évaluation Ultralytics
elle-même nécessite un modèle entraîné (hors périmètre CI).
"""
import json
import shutil

import numpy as np
import pytest

from core.real_validation import (
    auto_evaluate_if_available,
    build_val_data_yaml,
    check_real_val_set,
    evaluate_real_map,
    find_train_leakage,
    list_images,
    save_report,
    validate_label_file,
)


@pytest.fixture
def real_val(tmp_path):
    """Set réel minimal : 2 photos annotées, 1 sans label."""
    cv2 = pytest.importorskip("cv2")
    root = tmp_path / "real_val"
    (root / "images").mkdir(parents=True)
    (root / "labels").mkdir()

    rng = np.random.default_rng(0)
    for name in ["photo_001", "photo_002", "photo_003"]:
        img = (rng.random((240, 320, 3)) * 255).astype(np.uint8)
        cv2.imwrite(str(root / "images" / f"{name}.jpg"), img)
    (root / "labels" / "photo_001.txt").write_text(
        "0 0.5 0.5 0.3 0.4\n1 0.25 0.25 0.2 0.2\n", encoding="utf-8")
    (root / "labels" / "photo_002.txt").write_text("", encoding="utf-8")
    # photo_003 : volontairement sans label
    return root


class TestValidateLabelFile:
    def test_valid_file(self, tmp_path):
        p = tmp_path / "ok.txt"
        p.write_text("0 0.5 0.5 0.2 0.3\n3 0.1 0.9 0.1 0.1\n", encoding="utf-8")
        assert validate_label_file(str(p)) == []

    def test_empty_file_is_valid(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("", encoding="utf-8")
        assert validate_label_file(str(p)) == []

    def test_wrong_field_count(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("0 0.5 0.5 0.2\n", encoding="utf-8")
        assert any("champs" in e for e in validate_label_file(str(p)))

    def test_non_numeric(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("zero 0.5 0.5 0.2 0.3\n", encoding="utf-8")
        assert any("numériques" in e for e in validate_label_file(str(p)))

    def test_out_of_range_coords(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("0 1.5 0.5 0.2 0.3\n", encoding="utf-8")
        assert any("[0,1]" in e for e in validate_label_file(str(p)))

    def test_bbox_overflows_image(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("0 0.95 0.5 0.3 0.3\n", encoding="utf-8")
        assert any("déborde" in e for e in validate_label_file(str(p)))

    def test_class_out_of_range(self, tmp_path):
        p = tmp_path / "bad.txt"
        p.write_text("7 0.5 0.5 0.2 0.3\n", encoding="utf-8")
        assert validate_label_file(str(p), num_classes=5)
        assert validate_label_file(str(p), num_classes=10) == []


class TestCheckRealValSet:
    def test_counts_and_ready(self, real_val):
        status = check_real_val_set(str(real_val))
        assert status["total_images"] == 3
        assert status["labeled"] == 2          # photo_002 vide = annotée valide
        assert status["unlabeled_files"] == ["photo_003.jpg"]
        assert status["invalid_labels"] == {}
        assert status["ready"] is True

    def test_empty_set_not_ready(self, tmp_path):
        status = check_real_val_set(str(tmp_path / "nowhere"))
        assert status["total_images"] == 0
        assert status["ready"] is False

    def test_invalid_label_blocks_ready(self, real_val):
        (real_val / "labels" / "photo_001.txt").write_text(
            "0 5 5 5\n", encoding="utf-8")
        status = check_real_val_set(str(real_val))
        assert "photo_001.txt" in status["invalid_labels"]
        assert status["ready"] is False


class TestLeakageGuard:
    def test_no_leak(self, real_val, tmp_path):
        train_dir = tmp_path / "train_images"
        train_dir.mkdir()
        assert find_train_leakage(str(real_val), [str(train_dir)]) == []

    def test_detects_exact_copy(self, real_val, tmp_path):
        train_dir = tmp_path / "train_images"
        train_dir.mkdir()
        # copie exacte d'une photo réelle dans le train, sous un autre nom
        shutil.copy(str(real_val / "images" / "photo_001.jpg"),
                    str(train_dir / "sneaky_layout_042.jpg"))
        leaks = find_train_leakage(str(real_val), [str(train_dir)])
        assert len(leaks) == 1
        assert leaks[0][0].endswith("photo_001.jpg")

    def test_missing_train_dir_ignored(self, real_val):
        assert find_train_leakage(str(real_val), ["/nonexistent/dir"]) == []


class TestDataYamlAndReport:
    def test_build_val_data_yaml(self, real_val):
        import yaml
        path = build_val_data_yaml(str(real_val), ["Pika_Chu", "Dracaufeu"])
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["nc"] == 2
        assert data["names"] == ["Pika_Chu", "Dracaufeu"]
        assert data["val"] == "images"

    def test_save_report_appends_history(self, tmp_path):
        report = tmp_path / "report.json"
        save_report({"real_mAP50": 0.5, "timestamp": "t1"}, str(report))
        save_report({"real_mAP50": 0.7, "timestamp": "t2"}, str(report))
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["latest"]["real_mAP50"] == 0.7
        assert [h["real_mAP50"] for h in data["history"]] == [0.5, 0.7]

    def test_save_report_recovers_from_corrupt_file(self, tmp_path):
        report = tmp_path / "report.json"
        report.write_text("{pas du json", encoding="utf-8")
        save_report({"real_mAP50": 0.4}, str(report))
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["latest"]["real_mAP50"] == 0.4


class TestEvaluateGuards:
    def test_skips_when_set_empty(self, tmp_path):
        logs = []
        out = evaluate_real_map("model.pt", real_root=str(tmp_path / "none"),
                                log=logs.append)
        assert out is None
        assert any("vide" in line or "sauté" in line for line in logs)

    def test_refuses_on_leak(self, real_val, tmp_path, monkeypatch):
        import core.real_validation as rv
        train_dir = tmp_path / "train_images"
        train_dir.mkdir()
        shutil.copy(str(real_val / "images" / "photo_001.jpg"),
                    str(train_dir / "leak.jpg"))
        monkeypatch.setattr(rv, "DEFAULT_TRAIN_DIRS", [str(train_dir)])
        logs = []
        out = rv.evaluate_real_map("model.pt", real_root=str(real_val),
                                   log=logs.append)
        assert out is None
        assert any("FUITE" in line for line in logs)

    def test_auto_evaluate_never_raises(self, tmp_path):
        """Contrat TrainingManager : ne doit jamais faire échouer le train."""
        logs = []
        out = auto_evaluate_if_available("missing_model.pt",
                                         log=logs.append,
                                         real_root=str(tmp_path / "none"))
        assert out is None


class TestListImages:
    def test_extensions_and_sorting(self, tmp_path):
        cv2 = pytest.importorskip("cv2")
        img = np.zeros((10, 10, 3), np.uint8)
        for name in ["b.jpg", "a.png", "c.txt", "d.jpeg"]:
            p = tmp_path / name
            if name.endswith(".txt"):
                p.write_text("x")
            else:
                cv2.imwrite(str(p), img)
        names = [p.split("/")[-1] for p in list_images(str(tmp_path))]
        assert names == ["a.png", "b.jpg", "d.jpeg"]
